build command 
```bash
poetry build-project -v -C projects/fapi_example --clean -o dist
```

docker command 
```bash
docker build -t registry.localhost:5001/fapi-example:local projects/fapi_example
docker push registry.localhost:5001/fapi-example:local
```

kubernetes commands   
apply
```bash
kubectl apply -f projects/fapi_example/kubernetes/local/all.yaml
```
delete
```bash
kubectl delete -f projects/fapi_example/kubernetes/local/all.yaml