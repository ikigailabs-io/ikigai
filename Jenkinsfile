pipeline {
    agent {
        kubernetes {
            label 'jenkins-jenkins-agent'
            customWorkspace "/home/jenkins/agent/workspace/up/${env.BUILD_NUMBER}"
        }
    }

    stages{
        stage('Checkout') {
            steps{
                checkout scm
            }
        }
    }
}
