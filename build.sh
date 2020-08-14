docker build -t st:app .
az acr build --registry spotlit --image st:app .