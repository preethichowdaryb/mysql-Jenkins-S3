pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }

  environment {
    DB_HOST   = '127.0.0.1'
    DB_PORT   = '3306'
    DB_USER   = 'etl_user'
    DB_NAME   = 'company_db'
    AWS_REGION= 'us-east-1'
    S3_BUCKET = 'sql-s3-bucket-1'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Setup Python') {
      steps {
        sh '''
          set -e
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }
    stage('Run ETL') {
      environment {
        DB_PASSWORD = credentials('mysql_password')
        // AWS creds only if no IAM role
        // AWS_ACCESS_KEY_ID     = credentials('aws_access_key_id')
        // AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')
      }
      steps {
        sh '''
          set -e
          . .venv/bin/activate
          DB_HOST=${DB_HOST} DB_PORT=${DB_PORT} DB_USER=${DB_USER} DB_PASSWORD=${DB_PASSWORD} \
          DB_NAME=${DB_NAME} AWS_REGION=${AWS_REGION} S3_BUCKET=${S3_BUCKET} \
          python etl_mysql_to_s3.py | tee etl.log
        '''
      }
      post {
        always { archiveArtifacts artifacts: 'etl.log', fingerprint: true, onlyIfSuccessful: false }
      }
    }
  }
}
