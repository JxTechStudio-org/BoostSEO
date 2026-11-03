// BoostSEO CI/CD (Multibranch Pipeline job "boostseo").
//
// Every branch and PR: backend pytest, frontend lint + build, docker build of both images.
// CI images get their own boostseo-ci-* tags and are removed afterwards, so they never touch
// the boostseo-boostseo-* images the live containers run.
//
// production branch only: deploy with docker compose from this workspace (project name is
// pinned to "boostseo" in docker-compose.yml), health check the public site, and on failure
// redeploy the previous images (tagged :rollback before the deploy) and fail the build.

def PUBLIC_URL = 'https://boostseo.jxtechstudio.com'
def COMMENTS_VOLUME = 'boostseo_boostseo-comments-data'
def SERVICES = ['boostseo-backend', 'boostseo-frontend']

// Returns 0 when / and /api/docs both answer 200, retrying for about a minute.
def healthCheck(String baseUrl) {
  return sh(returnStatus: true, script: """
    set -u
    for attempt in \$(seq 1 12); do
      root=\$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 '${baseUrl}/' || true)
      docs=\$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 '${baseUrl}/api/docs' || true)
      echo "Health check attempt \$attempt: / -> \$root, /api/docs -> \$docs"
      if [ "\$root" = 200 ] && [ "\$docs" = 200 ]; then
        exit 0
      fi
      sleep 5
    done
    exit 1
  """)
}

pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Prepare') {
      steps {
        script {
          // Docker tags must be lowercase; branch names like PR-12 are not.
          env.CI_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}".toLowerCase().replaceAll(/[^a-z0-9_.-]/, '-')
        }
        echo "CI image tag: ${env.CI_TAG}"
        sh 'docker compose config --quiet'
      }
    }

    stage('CI') {
      parallel {
        stage('Backend: pytest') {
          steps {
            sh '''
              set -eu
              docker build --target test -f backend/Dockerfile -t "boostseo-ci-backend-test:$CI_TAG" .
              # Tests use TestClient and tmp_path only; no network needed.
              docker run --rm --network none "boostseo-ci-backend-test:$CI_TAG"
            '''
          }
        }

        stage('Frontend: lint + build') {
          steps {
            sh '''
              set -eu
              # The builder stage runs npm install + npm run build.
              docker build --target builder -t "boostseo-ci-frontend-builder:$CI_TAG" frontend
              docker run --rm "boostseo-ci-frontend-builder:$CI_TAG" npm run lint
            '''
          }
        }

        stage('Docker: production images') {
          steps {
            sh '''
              set -eu
              docker build --target production -f backend/Dockerfile -t "boostseo-ci-backend:$CI_TAG" .
              docker build -t "boostseo-ci-frontend:$CI_TAG" frontend

              # The production backend image must not ship the tests or pytest.
              docker run --rm "boostseo-ci-backend:$CI_TAG" sh -c \
                'test ! -e /app/tests && ! python -c "import pytest" 2>/dev/null' \
                || { echo "Production backend image contains tests or pytest"; exit 1; }
            '''
          }
        }
      }
    }

    stage('Deploy') {
      when { branch 'production' }
      steps {
        sh """
          set -eu
          # Never let compose create the comments volume: it must already exist.
          docker volume inspect ${COMMENTS_VOLUME} >/dev/null 2>&1 \
            || { echo 'Volume ${COMMENTS_VOLUME} not found; refusing to deploy.'; exit 1; }
        """

        script {
          // Tag the images the live containers run, so a failed deploy can go back to them.
          def rollbackReady = true
          for (svc in SERVICES) {
            def tagged = sh(returnStatus: true, script: """
              set -eu
              image_id=\$(docker inspect -f '{{.Image}}' ${svc})
              docker tag "\$image_id" boostseo-${svc}:rollback
              echo "Tagged running ${svc} image \$image_id as boostseo-${svc}:rollback"
            """)
            if (tagged != 0) {
              rollbackReady = false
              echo "WARNING: no running ${svc} container to tag; automatic rollback is unavailable."
            }
          }

          def upStatus = sh(returnStatus: true, script: 'docker compose up -d --build')
          def healthy = (upStatus == 0) && healthCheck(PUBLIC_URL) == 0

          if (!healthy) {
            if (!rollbackReady) {
              error('Deploy failed and there are no previous images to roll back to.')
            }
            echo 'Deploy failed; rolling back to the previous images.'
            sh """
              set -eu
              for svc in ${SERVICES.join(' ')}; do
                docker tag boostseo-\$svc:rollback boostseo-\$svc:latest
              done
              docker compose up -d --no-build --force-recreate
            """
            if (healthCheck(PUBLIC_URL) == 0) {
              error('Deploy failed its health check; rolled back to the previous images.')
            }
            error('Deploy failed its health check, and the site is still unhealthy after rolling back.')
          }
        }
      }
    }
  }

  post {
    always {
      sh '''
        docker image rm -f \
          "boostseo-ci-backend-test:$CI_TAG" \
          "boostseo-ci-frontend-builder:$CI_TAG" \
          "boostseo-ci-backend:$CI_TAG" \
          "boostseo-ci-frontend:$CI_TAG" >/dev/null 2>&1 || true
      '''
    }
    success {
      echo 'BoostSEO pipeline completed successfully.'
    }
    failure {
      echo 'BoostSEO pipeline failed. Check the stage logs above for details.'
    }
  }
}
