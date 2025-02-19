script {
    def logLines = currentBuild.rawBuild.getLog(100).join('\n')
    emailext(
        to: 'lhaynie@santaclarautah.gov, rlevsey@santaclarautah.gov',
        subject: "Build Fixed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
        body: """
            <strong>Project:</strong> ${env.JOB_NAME}<br>
            <strong>Build Number:</strong> ${env.BUILD_NUMBER}<br>
            <strong>Result:</strong> ${currentBuild.currentResult}<br>
            <strong>URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br><br>
            <strong>Last 100 lines of build log:</strong>
            <pre>${logLines}</pre>
            """,
        mimeType: 'text/html'
    )
}