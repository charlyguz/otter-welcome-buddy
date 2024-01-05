<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="images/nutria_logo.png">
  <h2 align="center">Otter ... Welcome Buddy</h2>
  <p align="center">
    Bot to help the management of Proyecto Nutria's discord
  <br />
  <a href="https://github.com/Proyecto-Nutria/otter-welcome-buddy/issues">Report Bug</a>
  </p>
  <br />
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

Otter Welcome Buddy has the intention of leverage human interaction with the persons in the discord to help them navigate trough all of our resources.
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

You need to install all the prerequisites before following with the instalation **except Tox**.

1. [Precommit](https://pre-commit.com/#installation)
1. [Poetry](https://python-poetry.org/)
1. [Tox](https://tox.wiki/en/latest/)
1. [Docker](https://docs.docker.com/get-docker/)

### Installation
1. Install our precommits configuration
   ```sh
   pre-commit install
   ```
1. Install all the dependencies for python
   ```sh
   poetry install
   ```
1. Install tox inside poetry's env
    ```sh
    poetry shell # activate poetry env
    pip install tox
    ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONFIGURATION INSTRUCTIONS -->
## Configuration

You need the following environmental variables either in a `.env` file under the root directory of this repository or directly added at your system (or your Docker instance):

* `DISCORD_TOKEN`: the Discord Bot Token retrieved from the [developer page](https://discord.com/developers/applications).
* `MONGO_URI`: address of the [MongoDB](https://docs.mongodb.com/manual/reference/connection-string/) instance to be used, could be local or [Cluster from Atlas](https://www.mongodb.com/cloud/atlas).


<!-- DOCKER INSTRUCTIONS -->
### Dockerize

If you want to use [`Docker`](https://www.docker.com/) with [`Docker-Compose`](https://docs.docker.com/compose/), you need to take care of few extra steps.

#### Dependencies

Be sure to have this two technologies installed:

* [Docker Engine](https://docs.docker.com/engine/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)

#### Environment Variables

Add these variables in the "environment" (`.env`) file (additional to the ones required on the [Configuration section](#configuration)).

- **MONGO_ROOT_USERNAME**: username to be created as root user with given credentials to manage MongoDB.
- **MONGO_ROOT_PASSWORD**: strong password to be used as credentials for `MONGO_ROOT_USERNAME`.
- **MONGO_USERNAME**: user that manage the connections of the application into the database.
- **MONGO_PASSWORD**: credentials configured to the user of the application.

> :warning: You can omit **MONGO_URI** because will be configured during the creation.

#### Run

```sh
# Build and run the bot
docker-compose up -d
```


<!-- USAGE EXAMPLES -->
## Usage

1. Activate your virtual environment
   ```sh
      poetry shell
   ```
1. Run the bot using:
   ```sh
    poetry run python otter_welcome_buddy
   ```
1. If you would like to run the build locally:
   ```sh
    tox
   ```

<!-- ROADMAP -->
## Roadmap

- [ ] Link the repository to our project dashboard
- [ ] Add deepsource
- [ ] Add vale
- [ ] Enable logging

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

This README was possible thanks to [Best-README](https://github.com/othneildrew/Best-README-Template)


<p align="right">(<a href="#readme-top">back to top</a>)</p>
