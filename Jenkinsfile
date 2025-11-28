pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'SonarQubeScanner' 
        NVD_API_KEY = credentials('nvdApiKey')
        TARGET_URL = "http://mysql-db:5000" 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Instalar Dependencias') {
            steps {
                echo "Instalando dependencias..."
                sh 'pip install -r requirements.txt --break-system-packages'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('Sonar-Server') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=pipeline-test -Dsonar.sources=. -Dsonar.python.version=3"
                    }
                }
            }
        }

        stage('OWASP Dependency-Check') {
            steps {
                dependencyCheck additionalArguments: "--format HTML --format XML --noupdate --nvdApiKey ${NVD_API_KEY}", odcInstallation: 'DependencyCheck'
            }
            post {
                always {
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true, reportDir: '.', reportFiles: 'dependency-check-report.html', reportName: 'Dependency-Check Report'])
                }
            }
        }
        
        stage('OWASP ZAP (DAST Scan)') {
            steps {
                sh '''
                docker run --network="jenkins-net" --rm \
                zaproxy/zap-stable zap-baseline.py \
                -t http://mysql-db:5000/ \
                -r zap_report.html || true
                '''
            }
            post {
                always {
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: true, keepAll: true, reportDir: '.', reportFiles: 'zap_report.html', reportName: 'OWASP ZAP Security Report'])
                }
            }
        }
    }
}
