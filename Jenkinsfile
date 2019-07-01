pipeline {
    agent { docker { image 'python:3.5.3' } }
    stages {
        stage('build') {
            steps {
                sh 'pip3 install -r requirements.txt'
                sh 'pip3 install pytest'
            }
        }
        stage('test') {
            steps {
                sh 'pytest'
            }   
        }
    }
}
