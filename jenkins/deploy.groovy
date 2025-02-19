withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
    sh '''
    commit_hash=$(cat commit_hash.txt)
    branch=$(cat branch.txt)

    namespace="spillman"
    container="spillman-api"
    image="sccity/spillman-api"

    if [ "$branch" = "dev" ]; then
        DEPLOYMENT="spillman-api-dev"
    elif [ "$branch" = "prod" ]; then
        DEPLOYMENT="spillman-api"
    else
        echo "Error: Unknown branch '$branch'. Skipping deployment."
        exit 1
    fi

    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl

    echo "KUBECONFIG: $KUBECONFIG"

    ./kubectl get deployments -n $namespace

    ./kubectl --kubeconfig=$KUBECONFIG -n $namespace \
        set image "deployment/$DEPLOYMENT" \
        "$container=$image:$commit_hash-$branch"

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes Update Failed!"
        exit 1
    fi

    ./kubectl -n $namespace --kubeconfig $KUBECONFIG \
        rollout status deployment/$DEPLOYMENT \
        -n $namespace

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes Rollout Failed!"
        exit 1
    fi
    '''
}