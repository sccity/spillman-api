withCredentials([usernamePassword(credentialsId: 'git', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
    sh '''
    git fetch --tags --prune --all

    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

    if [ "$branch" = "HEAD" ]; then
        branch=$(git for-each-ref --sort=-committerdate refs/remotes/origin/ --format="%(refname:short)" | grep -v 'HEAD' | head -n 1 | awk -F'/' '{print $2}')
    fi

    commit_hash=$(git rev-parse --short HEAD)

    echo "Branch: ${branch} - Commit Hash: $commit_hash"

    git config --global user.email "jenkins@email.santaclarautah.gov"
    git config --global user.name "Jenkins"

    if git ls-remote --tags origin | grep -q "refs/tags/$commit_hash"; then
        echo "Tag $commit_hash already exists. Skipping tag creation."
    else
        echo "Creating and pushing Git tag: $commit_hash"

        GIT_ASKPASS=$(mktemp)
        echo '#!/bin/sh' > $GIT_ASKPASS
        echo 'echo "$GIT_PASSWORD"' >> $GIT_ASKPASS
        chmod +x $GIT_ASKPASS

        git tag -a "$commit_hash" -m "Automated Build $commit_hash"
        GIT_ASKPASS=$GIT_ASKPASS git push origin tag "$commit_hash"

        rm -f $GIT_ASKPASS
    fi

    echo $commit_hash > commit_hash.txt
    echo $branch > branch.txt
    '''
}