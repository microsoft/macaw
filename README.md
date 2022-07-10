# Macaw: An Extensible Conversational Information Seeking Platform

Conversational information seeking (CIS) has been recognized as a major emerging research area in information retrieval.
Such research will require data and tools, to allow the implementation and study of conversational systems. Macaw is an
open-source framework with a modular architecture for CIS research. Macaw supports _multi-turn_, _multi-modal_, and
_mixed-initiative_ interactions, for tasks such as document retrieval, question answering, recommendation, and
structured data exploration. It has a modular design to encourage the study of new CIS algorithms, which can be
evaluated in batch mode. It can also integrate with a user interface, which allows user studies and data collection in
an interactive mode, where the back end can be _fully algorithmic_ or a _wizard of oz_ setup.

Macaw could be of interest to the researchers and practitioners working on information retrieval, natural language
processing, and dialogue systems.

For more information on Macaw, please refer to [this paper](https://arxiv.org/pdf/1912.08904.pdf).

Table of content:

- [Macaw Architecture](#macaw-architecture)
  - [Interfaces](#interfaces)
  - [Retrieval](#retrieval)
  - [Answer Selection and Generation](#answer-selection-and-generation)
- [Installation](#installation)
- [Running Macaw](#running-macaw)
- [Bug Report and Feature Request](#bug-report-and-feature-request)
- [Citation](#citation)
- [License](#license)
- [Contribution](#contribution)

## Macaw Architecture

Macaw has a modular architecture, which allows further development and extension. The high-level architecture of Macaw
is presented below:

![The high-level architecture of Macaw](macaw-arch.jpg)

For more information on each module in Macaw, refer to this paper.

#### Interfaces

Macaw supports the following interfaces:

- Standard IO: For _development_ purposes
- File IO: For _batch experiments_ (see the examples in the `data` folder for input and output file formats)
- Telegram bot: For interaction with real users

Here is an example of the Telegram interface for Macaw. It supports multi-modal interactions (text, speech, click, etc).

![Telegram interface for Macaw](macaw-example-tax.jpg)
![Telegram interface for Macaw](macaw-example-shakespeare.jpg)

#### Retrieval

Macaw features the following search engines:

- [Tantivy](https://github.com/quickwit-oss/tantivy): Tantivy is a full-text search engine library written in Rust.
- Bing web search API: sending a request to the Bing API and getting the results.

#### Answer Selection and Generation

For question answering, Macaw only features [the DrQA model](https://github.com/facebookresearch/DrQA) in its current
version.

## Installation and running with Docker

The package has been tested with certain dependencies and it is much easier to reproduce it in a similar environment. It
has been integrated with Docker to make it compatible with all operating systems. The default Docker setup runs the
application using the Standard IO interface, uses Tantivy for document retrieval, and DrQA for MRC (answer selection). To
run using other settings, appropriate changes should be done.

The first step is to install [Docker](https://docs.docker.com/engine/install/) in your system. Then continue with the
below steps.

### Create the build

To reduce the size of the build, we can keep certain data outside the Docker container and mount it
using [volumes](https://docs.docker.com/storage/volumes/).

1. Download the Stanford Core NLP data
   from [here](http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip) and put the
   directory `stanford-corenlp-full-2017-06-09` in your project root directory.
1. Install [DrQA](https://github.com/facebookresearch/DrQA) in a separate workspace and download the pre-trained model.
   It stores the models in `data/reader/` directory. We will use the downloaded _multitask.mdl_ model.

Once you have the two downloads done, run the below command from project root to create a docker build with name _macaw_:

```commandline
docker build -t macaw .
```

If you don't want to pre-install DrQA model and Stanford Core NLP data, create the build using the below command. It
will install both dependencies for you and keep them as part of the build. Note that this will significantly increase
the build size (by ~400MB for Stanford CoreNLP and by ~7.5GB for DrQA).

```commandline
docker build --build-arg download_stanford_corenlp=true --build-arg download_drqa_model=true -t macaw .
```

_Note: To make sure that the Docker container builds without modification, an x86_64/amd64 system is required. If you have an arm64 device, then add the flag `--platform linux/amd64` to the build command._

### Run the application

If you downloaded certain data locally, then use Docker volumes to mount local directory to Docker container. You need
to provide the local directory path during runtime. Run the command from project root.

```commandline
docker run --rm -i --name=macaw_test_container \
-v <path/to/DrQA/data>:/usr/src/app/DrQA/data \
-v $("pwd")/stanford-corenlp-full-2017-06-09:/usr/src/app/stanford-corenlp-full-2017-06-09 \
macaw
```

`</path/to/DrQA/data>` could be `/Users/amitgh/PycharmProjects/DrQA/data` if you downloaded the pre-trained model in a
separate workspace named DrQA.

If you did not separately download data at build time, simply run:

```commandline
docker run --rm -i --name=macaw_test_container macaw
```

In above command we start a container with name _macaw_test_container_ from build image _macaw_ in interactive
mode (`-i`)
and remove the container when the application exits (`--rm`). After installing all dependencies, it
runs `scripts/start.sh`
which first starts MongoDB server in a separate thread and then runs `live_main.py`.

_Note: Similar to requiring the additional flag of `--platform linux/amd64` to build the Docker container with an arm64 machine, running said container also requires the same flag.
:warning: **The performance of the container under this emulation will be incredibly poor. If possible, use a x86_64/amd64 system**._

#### Run with file input

To avoid typing the input every time, you can provide an input file and get output in an output file. We need to mount
the directory containing the data.

```commandline
docker build -t macaw . && docker run --rm -i --name=macaw_test_container \
-v <path/to/DrQA/data>:/usr/src/app/DrQA/data \
-v $("pwd")/stanford-corenlp-full-2017-06-09:/usr/src/app/stanford-corenlp-full-2017-06-09 \
-v $("pwd")/data:/usr/src/app/data \
macaw
```

Also update the command inside `scripts/start.sh` file to
```commandline
python3 macaw/live_main.py --mode exp --interface fileio
```

### ssh into the container

While the application is running, we can go inside the container to see the contents (directory structure, Tantivy index,
etc.).

```commandline
docker exec -it macaw_test_container /bin/bash
```

### Updating TREC data for Tantivy

Tantivy index is created using the document stored in `trec_documents/` directory. It has some default data. To create a
bigger index, download the entire data from [archive](https://archive.org/details/trec-ir) and put it in trec_documents.
Docker will copy it during build time and create a new index.

## Running entire Macuna application

Using `docker compose` we can start the main application and all other supporting docker containers (nlp pipeline
applications and remote modules) at once. This does not work with stdio mode as docker compose does not support
terminal input. Run the below command.

```commandline
docker compose build && docker compose up
```

To run different containers independently or to support terminal input, run the below commands in order.

First, build the application.

```commandline
docker compose build
```

Second, start all the supporting remote modules. Make sure to explicitly provide port and container names. This can be
found from the `docker-compose.yml` file.

```commandline
docker compose run --rm -p "127.0.0.1:8001:80" --name nlp-pipeline-app-flask nlp-pipeline-app-flask
docker compose run --rm -p "127.0.0.1:8002:80" --name nlp-pipeline-app-ic nlp-pipeline-app-ic
docker compose run --rm -p "127.0.0.1:8003:80" --name response-generator-app-qa response-generator-app-qa
```

Third, run the main application which has stdio (or it can also have fileio). For stdio update the flags in `start.sh`
with `--mode live --interface stdio`.

```commandline
docker compose run --rm base-app
```

## Local Setup

To setup the package locally without using Docker, follow the below instructions.

### Installation

Macaw requires `Python >= 3.5` and `pip3`. If you don't have `setuptools`, run `sudo pip3 install setuptools`. To
install Macaw, first **clone macaw** from this repo and then follow the following installation steps. The mentioned
installation commands can be executed on Ubuntu. You can use the same or similar commands on other Linux distribution.
If you are using Windows 10, we recommend installing Macaw and all the required packages on
[Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

#### Step 1: Installing MongoDB server

Macaw uses MongoDB for storing and retrieving user interactions (conversations). To install MongoDB server, run the
following command:

```
sudo apt-get install mongodb-server-core
```

At this step, you can make sure your installation is complete by running the pyndri tests.

#### Step 2: Installing Stanford Core NLP

Stanford Core NLP can be used for tokenization and most importantly for co-reference resolution. If you do not need
co-reference resolution, you can ignore this step. Stanford Core NLP requires `java`. Get it by following these
commands:

```
wget -O "stanford-corenlp-full-2017-06-09.zip" "http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip"
sudo apt-get install unzip
unzip "stanford-corenlp-full-2017-06-09.zip"
rm "stanford-corenlp-full-2017-06-09.zip"
```

If you don't have `java`, install it using:

```
sudo apt-get install default-jre
```

#### Step 3: Installing DrQA

Macaw also supports answer extraction / generation for user queries from retrieved documents. For this purpose, it
features [DrQA](https://github.com/facebookresearch/DrQA). If you do not need this functionality, ignore this step (you
can also install this later). To install DrQA, run the following commands:

```
git clone https://github.com/facebookresearch/DrQA.git
cd DrQA
pip3 install -r requirements.txt
pip3 install torch
sudo python3 setup.py develop
```

To use pre-trained DrQA model, use the following command.

```
./download.sh
```

This downloads a 7.5GB (compressed) file and requires 25GB (uncompressed) space. This may take a while!

#### Step 4: Installing FFmpeg

To support speech interactions with users, Macaw requires FFmpeg for some multimedia processing steps. If you don't need
a speech support from Macaw, you can skip this step. To install FFmpeg, run the following command:

```
sudo apt-get install
```

#### Step 5: Installing Macaw

After cloning Macaw, use the following commands for installation:

```
cd macaw
sudo pip3 install -r requirements.txt
sudo python3 setup.py install
```

### Running Macaw

If you run macaw with interactive (or live) mode, you should first run MongoDB server using the following command:

```
sudo mongod
```

Note that this command uses the default database directory (`/data/db`) for storing the data. You may need to create
this directory if you haven't. You can also use other locations using the `--dbpath` argument.

We provide three different main scripts (i.e., app):

- `live_main.py`: An interactive conversational search and question answering system. It can use both STDIO and Telegram
  interfaces.
- `batch_ext_main.py`: A model for running experiments on a reusable dataset. This main script uses FILEIO as the
  interface.
- `wizard_of_oz_main.py`: A main script for Wizard of Oz experiments.

After selecting the desired main script, open the python file and provide the required parameters. For example, you need
to use your Bing subscription key (if using Bing), the path to Tantivy index, Telegram bot token (if
using Telegram interface), etc. in order to run the `live_main.py` script. You can further run the favorite main script
as below:

```
python3 live_main.py
```

## Bug Report and Feature Request

For bug report and feature request, you can open an issue in github, or send an email to
[Hamed Zamani](http://hamedz.ir) at `hazamani@microsoft.com`.

## Citation

If you found Macaw useful, you can cite the following article:

```
Hamed Zamani and Nick Craswell, "Macaw: An Extensible Conversational Information Seeking System", arxiv pre-print.
```

bibtex:

```
@article{macaw,
  title={Macaw: An Extensible Conversational Information Seeking Platform},
  author={Zamani, Hamed and Craswell, Nick},
  journal={arXiv preprint arXiv:1912.08904},
  year={2019},
}
```

## License

Macaw is distributed under the **MIT License**. See the `LICENSE` file for more information.

## Contribution

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License
Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For
details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate
the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
