# IncidentLab + DeployDoctor

IncidentLab is a Django-based web application for practicing production incidents and learning how to diagnose common deployment problems. DeployDoctor analyzes deployment configuration and identifies potential issues with explanations and suggested fixes.

## Features

### IncidentLab
- Practice realistic production incident scenarios.
- Review logs, metrics, and deployment configuration.
- Submit answers and receive scores.
- Learn from explanations and lessons.

### DeployDoctor
- Analyze deployment configuration files.
- Detect common deployment issues using rule-based checks.
- Show issue severity, explanations, and suggested fixes.

## Technology Stack

- Python
- Django
- HTML and CSS
- Gunicorn
- WhiteNoise
- AWS Elastic Beanstalk
- Git and GitHub

## Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/Srimaha02/incidentlab.git
   cd incidentlab
   ```

2. Create and activate a virtual environment.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the required environment variables, including `SECRET_KEY` and `ALLOWED_HOSTS`.

5. Run database migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Open `http://127.0.0.1:8000/` in your browser.

## Testing

Run the automated tests:

```bash
python manage.py test
```

Check the Django configuration:

```bash
python manage.py check
```

## Deployment

The application is deployed on AWS Elastic Beanstalk using Gunicorn and WhiteNoise for static files.

The deployment includes a health endpoint at `/health/` and a pre-deployment hook to collect static files.

## Project Status

- Incident practice flow tested.
- DeployDoctor configuration analysis tested.
- Static files served successfully in production.
- AWS Elastic Beanstalk environment reported healthy.
- Standard Elastic Beanstalk hostname has a DNS resolution issue under investigation.

## Security Notes

- Keep `SECRET_KEY` in environment variables.
- Never commit secrets or credentials to GitHub.
- Keep `DEBUG` disabled in production.
