withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
    sh '''
    commit_hash=$(cat commit_hash.txt)
    branch=$(cat branch.txt)

    image=sccity/spillman-api

    if [ -z "$commit_hash" ]; then
        echo "Error: Commit hash file is missing!"
        exit 1
    fi

    yq -iY '.version = "$commit_hash"' spillman/version.yaml

    echo "Using Commit Hash: $commit_hash for Docker build"
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

    rm -fR config/settings.yaml

    docker build --platform linux/x86_64 -t $image:$commit_hash-$branch --push .

    if [ $? -ne 0 ]; then
        echo "Error: Docker latest tag push failed!"
        exit 1
    fi
    '''
}