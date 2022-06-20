from app import create_app

app = create_app()


@app.route('/')
def root():
    """
    this is the root of the api
    later on we need to create a
    root template for the api.
    """

    return "Welcome to floExpenseTracker"


if __name__ == "__main__":
    app.run()