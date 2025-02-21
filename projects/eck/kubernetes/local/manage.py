from managment.tools.core import  create_parser, execute_command, kubectl_operation, kubectl_apply_manifest, kubectl_delete_manifest, run_command


ECK_VERSION = "2.16.1"
CRDS_URL = f"https://download.elastic.co/downloads/eck/{ECK_VERSION}/crds.yaml"
OPERATOR_URL = f"https://download.elastic.co/downloads/eck/{ECK_VERSION}/operator.yaml"
ELK_NAME = "elk"
ELK_NAMESPACE = "default"
ELK_VERSION = "8.17.2"
ELK_MANIFEST = f"""apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: {ELK_NAME}
  namespace: {ELK_NAMESPACE}
spec:
  version: {ELK_VERSION}
  nodeSets:
  - name: default
    count: 1
    config:
      node.store.allow_mmap: false
  http:
    tls:
      selfSignedCertificate:
        disabled: true
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: elastic
  namespace: {ELK_NAMESPACE}
spec:
  rules:
    - host: elastic.localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {ELK_NAME}-es-http
                port:
                  number: 9200
"""

KIBANA_MANIFEST = f"""apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: {ELK_NAME}
  namespace: {ELK_NAMESPACE}
spec:
  version: {ELK_VERSION}
  count: 1
  elasticsearchRef:
    name: {ELK_NAME}
  http:
    tls:
      selfSignedCertificate:
        disabled: true
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kibana
  namespace: {ELK_NAMESPACE}
spec:
  rules:
    - host: kibana.localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {ELK_NAME}-kb-http
                port:
                  number: 5601
"""
"""
TODO: something wrong with this block
---
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
config:
  xpack.fleet.packages:
  - name: apm
    version: latest
"""
APM_MANIFEST = f"""apiVersion: apm.k8s.elastic.co/v1
kind: ApmServer
metadata:
  name: {ELK_NAME}
  namespace: {ELK_NAMESPACE}
spec:
  version: {ELK_VERSION}
  count: 1
  elasticsearchRef:
    name: {ELK_NAME}
  kibanaRef:
    name: {ELK_NAME}
  http:
    tls:
      selfSignedCertificate:
        disabled: true
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: apm-server
  namespace: {ELK_NAMESPACE}
spec:
  rules:
    - host: apm.localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {ELK_NAME}-apm-http
                port:
                  number: 8200
"""

def apply_command(args):
    print(f"Applying with arguments: {args}")
    kubectl_operation("create", CRDS_URL)
    kubectl_operation("apply", OPERATOR_URL)
    run_command("kubectl wait --for=condition=Ready pod/elastic-operator-0 -n elastic-system --timeout=60s")
    kubectl_apply_manifest(ELK_MANIFEST)
    # run_command("kubectl wait --for=condition=Ready $(kubectl get pods -n default -o name | grep quickstart-es-default) -n default --timeout=20s")
    # run_command("kubectl get secret quickstart-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'")
    kubectl_apply_manifest(APM_MANIFEST)
    kubectl_apply_manifest(KIBANA_MANIFEST)
    # run_command("kubectl wait --for=condition=Ready $(kubectl get pods -n default -o name | grep quickstart-kb) -n default --timeout=20s")
    # run_command("kubectl get secret quickstart-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode; echo")

def delete_command(args):
    print(f"Deleting with arguments: {args}")
    kubectl_delete_manifest(ELK_MANIFEST)
    kubectl_delete_manifest(KIBANA_MANIFEST)
    kubectl_delete_manifest(APM_MANIFEST)
    kubectl_operation("delete", CRDS_URL)
    kubectl_operation("delete", OPERATOR_URL)

def main():
    parser, subparsers = create_parser("Tool with apply and delete commands for eck and elk.")  # Get both
    subparsers.choices["apply"].set_defaults(func=apply_command)
    subparsers.choices["delete"].set_defaults(func=delete_command)

    args = parser.parse_args()
    execute_command(parser, args)


if __name__ == "__main__":
    main()