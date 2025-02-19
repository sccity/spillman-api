withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
    sh '''
    commit_hash=$(cat commit_hash.txt)
    branch=$(cat branch.txt)

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

    ./kubectl --kubeconfig $KUBECONFIG \
        set image deployment/$DEPLOYMENT \
        spillman-api=sccity/spillman-api:$commit_hash \
        -n spillman

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes update failed!"
        exit 1
    fi

    ./kubectl --kubeconfig $KUBECONFIG \
        rollout status deployment/$DEPLOYMENT \
        -n spillman

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes rollout failed!"
        exit 1
    fi
    '''
}