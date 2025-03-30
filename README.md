# Introduction 
Welcome to extraction keyword microservice.

This is a simple api that use keyword extraction developped by the data scientist team.

# Getting Started

**IMPORTANT**: To be able to install the **ranking_features** package that is stored in Azure DevOps, you need to generate an access token by going to User settings > Personal Access Tokens > New Token and creating a new token with read permissions for the Packaging scope.

## To run the code locally
1. Create a virtual env and activate it:
   - conda create --name ms-keyword-extraction --python=3.10
   - conda activate ms-keyword-extraction
2. Run `pip install -r requirements.txt` to install project dependencies.
3. Get ranking_features wheel file from https://gitcorpagileinfra.ent.cgi.com/groups/digit/digit_canda/-/packages/6 and put it in the root repo
4. Run `pip install ranking_features-0.2.3-py3-none-any.whl` to install the ranking-features library.
5. Get the data files from https://gitcorpagileinfra.ent.cgi.com/digit/digit_canda/digit_canda_ia/ms_ranking/-/packages/7, unzip it and put the *global_keywords_df.csv* in the data/ folder in the root repository.

This will allow you to download from Azure Artefact.

## To run the code from a docker/podman container:

1. Get ranking_features wheel file from https://gitcorpagileinfra.ent.cgi.com/groups/digit/digit_canda/-/packages/6 and put it in the root repo
2. Get the data files from https://gitcorpagileinfra.ent.cgi.com/digit/digit_canda/digit_canda_ia/ms_ranking/-/packages/7, unzip it and put the *global_keywords_df.csv* in the data/ folder in the root repository
3. Run `docker build -t ms-extraction .`
4. Run `docker run -it -p 8080:8080 --env-file .env ms-extraction`


# Build and Test

To run the unit tests:

1. Install the additional required packages `pip install pytest httpx`
2. Run `pytest test` from the root of the repo
# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)