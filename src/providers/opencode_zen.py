import requests

from .provider import Provider


class OpenCodeZen(Provider):
    def get_tag(self) -> str:
        return "opencode"

    def _get_models(self) -> list[str]:
        response = requests.get("https://opencode.ai/zen/v1/models")
        assert response.status_code == 200
        json_response = response.json()
        return [model_dict["id"] for model_dict in json_response["data"]]


if __name__ == "__main__":
    zen = OpenCodeZen()
    print(zen.get_models())
