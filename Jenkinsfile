pipeline {
    agent any

    environment {
         http_proxy="http://and-fgt-linux-01.akka.eu:9090"
         https_proxy="http://and-fgt-linux-01.akka.eu:9090"
         HTTP_PROXY="http://and-fgt-linux-01.akka.eu:9090"
         HTTPS_PROXY="http://and-fgt-linux-01.akka.eu:9090"
    }


    stages {
        
        stage('Test U') {
            steps {
                sh '''
                    date
                '''                                    
            }
        }

	stage('SonarQube analysis') {
		steps {
			withSonarQubeEnv('sonarqube'){
				sh '../../tools/hudson.plugins.sonar.SonarRunnerInstallation/sonar/bin/sonar-scanner'
			}
		}
	}
	
	stage('Deploy') {
            steps {
              sh '''
                    JENKINS_NODE_COOKIE=dontKillMe nohup python3 ./manage.py runserver 0.0.0.0:9000 &
                '''
            }
        }


    }
}
