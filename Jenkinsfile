pipeline {
    agent {
        kubernetes {
            label 'jenkins-jenkins-agent'
            customWorkspace "/home/jenkins/agent/workspace/up/${env.BUILD_NUMBER}"
        }
    }

    stages{
        stage('Setup Hatch') {
            steps{
                script{
                    def hatch_download_url = 'https://github.com/pypa/hatch/releases/latest/download/hatch-x86_64-unknown-linux-gnu.tar.gz'
                    // In future when this file is a bit stable then pass in cacheValidityDecidingFile
                    cache(
                        caches: [[
                            $class: 'ArbitraryFileCache',
                            path: '/tmp/hatch',
                            // cacheValidityDecidingFile: 'Jenkinsfile'
                        ]],
                        maxCacheSize: 512,
                    ) {
                        sh """
                        set +x
                        mkdir -p /tmp/hatch
                        echo 'Downloading hatch binary'
                        wget --output-document=/tmp/hatch/hatch.tar.gz ${hatch_download_url}
                        tar -zxvf /tmp/hatch/hatch.tar.gz -C /tmp/hatch
                        rm /tmp/hatch/hatch.tar.gz
                        echo 'Checking hatch binary'
                        /tmp/hatch/hatch --version
                        """
                    }

                    sh(
                        label: 'Installing Hatch',
                        script: '''
                        set +x
                        sudo mv /tmp/hatch/hatch /usr/local/bin/hatch
                        echo 'Checking hatch installation'
                        hatch --version
                        '''
                    )
                }
            }
        }
    }
}
