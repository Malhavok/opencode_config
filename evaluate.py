# Runs all specified models with a series of tasks, evaluating them.
import contextlib
import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import time
from enum import StrEnum
from typing import NamedTuple

CONFIG_FILE = "config.json"
PROMPT_FILE = "prompt.txt"
REVIEWER_MODEL = "ollama/gemma4:26b-nvfp4"
CACHE_DIR = pathlib.Path("./.evaluate_cache/")


class TaskLanguage(StrEnum):
    PYTHON = "python"


class TaskConfig(NamedTuple):
    language: TaskLanguage
    task_dir: pathlib.Path
    prompt_file: pathlib.Path
    result_file: pathlib.Path
    input_files: str
    timeout_seconds: float

    def copy_data(self, to_dir: pathlib.Path) -> None:
        shutil.copy(self.prompt_file, get_task_prompt(to_dir))
        for filename in self.input_files:
            source_path = (self.task_dir / filename).resolve()
            target_path = (to_dir / filename).resolve()
            shutil.copy(source_path, target_path)


def get_task_prompt(task_dir: pathlib.Path) -> pathlib.Path:
    return (task_dir / PROMPT_FILE).resolve()


def get_config(task_dir: pathlib.Path) -> TaskConfig:
    config_file = task_dir / CONFIG_FILE
    config_data = json.loads(config_file.read_text())

    return TaskConfig(
        language=TaskLanguage(config_data["language"]),
        task_dir=task_dir,
        prompt_file=(task_dir / config_data["prompt"]).resolve(),
        result_file=(task_dir / config_data["expected_result"]).resolve(),
        input_files=config_data["inputs"],
        timeout_seconds=config_data.get("timeout_minutes", 5) * 60,
    )


def prepare_python(target_dir: pathlib.Path) -> None:
    print(f"Building VENV at {target_dir}.")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "venv",
            str(target_dir / "venv"),
        ],
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    print("Done.")


def prompt_python(target_dir: pathlib.Path) -> str:
    return f"You have venv ready at {str(target_dir / 'venv')}, feel free to use it."


LANGUAGE_PREPARE = {
    TaskLanguage.PYTHON: prepare_python,
}

LANGUAGE_COMMAND = {
    TaskLanguage.PYTHON: prompt_python,
}


@contextlib.contextmanager
def build_task(task_dir: pathlib.Path):
    task_config = get_config(task_dir=task_dir)
    with tempfile.TemporaryDirectory() as dir:
        dir_path = pathlib.Path(dir)
        task_config.copy_data(dir_path)
        LANGUAGE_PREPARE[task_config.language](dir_path)
        yield dir_path, task_config


def run_model(
    dir_path: pathlib.Path, task_config: TaskConfig, model_name: str
) -> list[dict]:
    command = [
        f"Run the task using '{str(task_config.language)}' language.",
        LANGUAGE_COMMAND[TaskLanguage.PYTHON](dir_path),
        f"You have {task_config.timeout_seconds} seconds to solve this problem.",
    ]
    if len(task_config.input_files) > 0:
        command.append(
            f"Your task requires the following input files: {task_config.input_files}."
        )

    result = subprocess.run(
        [
            "opencode",
            "run",
            "--dangerously-skip-permissions",
            "--model",
            model_name,
            "--format",
            "json",
            "--dir",
            str(dir_path),
            "--message",
            get_task_prompt(task_dir=dir_path),
            " ".join(command),
        ],
        text=True,
        timeout=task_config.timeout_seconds,
        stdout=subprocess.PIPE,
        cwd=dir_path,
    )
    assert result.returncode == 0
    return [json.loads(line) for line in result.stdout.splitlines()]


def get_last_message(json_lines: list[dict]) -> str:
    text_lines = [line for line in json_lines if line["type"] == "text"]
    last_line = text_lines[-1]
    return last_line["part"]["text"]


def run_reviewer(
    dir_path: pathlib.Path,
    task_config: TaskConfig,
    task_result: list[dict],
) -> dict[str, object]:
    model_comms = dir_path / "_MODEL_COMMS.jsonl"
    model_comms.write_text("\n".join(json.dumps(elem) for elem in task_result))

    dimensions = [
        "validity",
        "simplicity",
        "explored_paths",
    ]
    example_json: dict[str, object] = {key: random.randint(0, 5) for key in dimensions}
    example_json["tokens"] = [
        {"input": 20_000, "output": 500, "reasoning": 0},
        {"input": 18_000, "output": 200, "reasoning": 0},
        {"input": 23_000, "output": 600, "reasoning": 0},
    ]

    command = [
        "You're reviewing the results of another agent work.",
        f"You're given {str(task_config.result_file)} that contains expected result,",
        f"{str(model_comms)} file that contains all the JSON communication with the model",
        f"and {str(task_config.prompt_file)} with the prompt the other agent received.",
        "Your goal is to validate the solution and rate it, on a scale from 0 to 5, where",
        "0 means that given dimension was not done at all, 1 means it was done poorly and"
        f"5 means it was done superb. Dimensions are: {', '.join(dimensions)}.",
        "In addition, you should report all the input, output and reasoning tokens used."
        "The last line in your response has to be a JSON all these keys mapped to the rating, e.g.",
        f"{json.dumps(example_json)}",
    ]

    result = subprocess.run(
        [
            "opencode",
            "run",
            "--dangerously-skip-permissions",
            "--model",
            REVIEWER_MODEL,
            "--format",
            "json",
            "--file",
            str(model_comms),
            "--file",
            str(task_config.result_file),
            "--file",
            str(task_config.prompt_file),
            "--dir",
            str(dir_path),
            " ".join(command),
        ],
        text=True,
        timeout=600,
        stdout=subprocess.PIPE,
        cwd=dir_path,
    )
    assert result.returncode == 0
    lines = [json.loads(line) for line in result.stdout.splitlines()]
    last_text = get_last_message(lines)
    last_line = last_text.splitlines()[-1]
    try:
        return json.loads(last_line)
    except json.JSONDecodeError:
        print("===")
        for line in lines:
            print(line)
        print("===")
        print(last_line)
        raise


def run_task(task_dir: pathlib.Path, model_name: str) -> dict[str, object]:
    with build_task(task_dir=task_dir) as (dir_path, task_config):
        print(dir_path)
        print([elem for elem in dir_path.glob("*")])

        print("=== Running model ===")
        time_start = time.time()
        model_output = run_model(dir_path, task_config, model_name)
        elapsed_seconds = time.time() - time_start
        for line in model_output:
            print(line)

        print("=== Running reviewer ===")
        result_dict = run_reviewer(
            dir_path=dir_path,
            task_config=task_config,
            task_result=model_output,
        )
        result_dict["elapsed_seconds"] = elapsed_seconds
        return result_dict


def list_models() -> list[str]:
    opencode_config = json.loads(pathlib.Path("./opencode/opencode.json").read_text())
    providers = opencode_config["provider"]
    models_list = []

    for name, config in providers.items():
        for model in config["models"].keys():
            models_list.append(f"{name}/{model}")

    return models_list


def get_cache_filename(task_dir: pathlib.Path, model_name: str) -> pathlib.Path:
    task_name = task_dir.parts[-1]
    replaced_chars = ["/", "-", ".", ":"]
    model_tag = model_name
    for char in replaced_chars:
        model_tag = model_tag.replace(char, "_")
    filename = f"{model_tag}__{task_name}"
    return CACHE_DIR / filename


def save_to_cache(
    task_dir: pathlib.Path, model_name: str, result: dict[str, object]
) -> None:
    get_cache_filename(task_dir=task_dir, model_name=model_name).write_text(str(result))


def is_in_cache(task_dir: pathlib.Path, model_name: str) -> bool:
    return get_cache_filename(task_dir=task_dir, model_name=model_name).exists()


def main() -> None:
    models = list_models()
    print(models)

    for task_dir in sorted(pathlib.Path("./tasks/").glob("*")):
        if not task_dir.is_dir():
            continue
        print(f"Running task at {task_dir}")

        for model in models:
            if is_in_cache(task_dir=task_dir, model_name=model):
                continue
            print(f"Running model {model}")

            result = run_task(
                task_dir=task_dir,
                model_name=model,
            )
            print(result)
            save_to_cache(task_dir=task_dir, model_name=model, result=result)


if __name__ == "__main__":
    main()
