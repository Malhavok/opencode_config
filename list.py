from src.providers import ALL_PROVIDERS


def main() -> None:
    for tag, provider in ALL_PROVIDERS.items():
        print(f"{tag}/")
        for model in provider.get_models():
            print(f"\t{model}")


if __name__ == "__main__":
    main()
