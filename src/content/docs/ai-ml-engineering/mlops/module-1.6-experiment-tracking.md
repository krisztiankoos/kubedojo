---
title: "Experiment Tracking"
slug: ai-ml-engineering/mlops/module-1.6-experiment-tracking
sidebar:
  order: 607
---
> **AI/ML Engineering Track** | Complexity: `[MEDIUM]` | Time: 5-6
## The Model That Vanished: A Cautionary Tale

**A late-night production incident.**

Sarah Chen stared at her laptop in disbelief. A production sentiment classifier had started returning unreliable predictions, even though the team believed they had deployed a well-performing model.

The investigation exposed a familiar failure mode: the team had no reliable record of which artifact had been deployed, who produced it, or how it related to earlier runs.

But which training run produced this model? Nobody knew. The training script existed in four different versions across three team members' laptops. The dataset could have been any of twelve different versions—the file was just called `training_data.csv` with no version information. The hyperparameters? Lost in a Jupyter notebook that had been overwritten countless times.

After failing to reconstruct the original setup, the team had to retrain from scratch and accept a model they could at least trace and explain.

Practitioners have repeatedly pointed to the same underlying problem: teams can train strong models, yet still struggle to reproduce them later or explain exactly how a production model was created.

Tools like MLflow emerged to make experiment history, model lineage, and reproducibility easier to manage.

This module teaches you how to prevent that kind of failure. You'll learn MLflow and Weights & Biases—two widely used experiment tracking tools—and how to build systems where model lineage and experiment metadata are recorded consistently.

---

## What You'll Be Able to Do

By the end of this module, you will:
- Master MLflow for experiment tracking, model versioning, and registry
- Learn Weights & Biases (W&B) for real-time experiment visualization and team collaboration
- Implement systematic experiment organization and tagging strategies
- Understand the MLOps maturity model and where your organization stands
- Deploy production-grade tracking infrastructure

---

## The Experiment Tracking Problem

### Why Experiment Tracking Matters

Machine learning development is fundamentally different from traditional software development. In traditional software, you write code, test it, and deploy it. The code IS the product. In ML, you train models—and the model is the product. The code is just a recipe.

This creates a unique problem. Traditional version control (Git) tracks code changes beautifully. But it's terrible at tracking:
- Which dataset version was used for training
- What hyperparameters produced the best model
- Which preprocessing steps were applied
- The random seed that made results reproducible
- The actual model weights (which can be gigabytes)

Think of it like a kitchen. Git can track your recipe (the code), but it can't track which specific tomatoes you used, what temperature your oven actually was (not what you set it to), or the skill of the chef on that particular day. In ML, all of these "environmental" factors matter—sometimes more than the recipe itself.

Without proper tracking, ML development degrades into chaos. Teams create folder structures that look like archaeological sites: `model_final.pt`, `model_final_v2.pt`, `model_final_ACTUALLY_FINAL.pt`, `model_best_USE_THIS.pt`. When the inevitable question comes—"Can we reproduce the model we shipped six months ago?"—the answer is usually a panicked silence.

**Did You Know?** Reproducibility initiatives in ML have highlighted a recurring problem: papers often omit details such as preprocessing steps, hyperparameters, and random seeds, which makes results hard to reproduce.

### The Hidden Cost of Poor Tracking

Poor experiment tracking creates a persistent maintenance burden: teams lose time reconstructing old runs, environments, and decisions instead of building new models. That's nearly half of an ML engineer's time spent not on building models, but on archaeology—digging through old experiments to figure out what was done before.

This cost compounds. Every time a team member leaves, institutional knowledge walks out the door. Every time a model needs updating, engineers must reconstruct the original training environment. Every time a stakeholder asks "why is this model behaving this way?", the answer requires hours of forensic investigation.

The solution is experiment tracking: systematically recording everything about every experiment, so any model can be reproduced, explained, and improved upon.

---

## 1. MLflow: The Open-Source Standard

### The Vision Behind MLflow

**Matei Zaharia** didn't set out to build an experiment tracking tool. He was trying to understand why ML teams at Databricks's customers were struggling to get models into production. The pattern was consistent: brilliant data scientists would build amazing models in notebooks, but those models would die in the handoff to production.

*"We realized the problem wasn't deployment,"* Zaharia explained in a 2019 interview. *"The problem was that nobody knew what they were deploying. The data scientist couldn't tell the ML engineer exactly which preprocessing steps were needed. The ML engineer couldn't tell operations which model version was in production. Everyone was guessing."*

MLflow was designed to solve this by treating experiment metadata with the same rigor that databases treat data: structured, queryable, and persistent.

The name "MLflow" comes from the concept of "workflow"—but specifically, the flow of machine learning experiments from conception to production. It's not just about tracking; it's about enabling the entire ML lifecycle.

### MLflow's Four Components

MLflow is actually four tools in one, each solving a different part of the ML lifecycle:

**MLflow Tracking** records experiments: parameters, metrics, artifacts, and source code. Every time you train a model, Tracking creates a "run" that captures everything about that training session. You can think of it as a flight recorder for your ML experiments—it captures everything so you can reconstruct what happened later.

**MLflow Projects** packages code in a reproducible format. Instead of sending a colleague a Python script and hoping it works on their machine, you package the code with its dependencies and entry points. Anyone can run the same experiment by pointing MLflow at the project.

**MLflow Models** provides a standard format for saving models. Different frameworks (PyTorch, TensorFlow, scikit-learn) save models differently. MLflow Models provides a unified format that any deployment tool can understand. It's like PDF for ML models—a broadly compatible format that works in many environments.

**MLflow Model Registry** provides versioning and lifecycle management for production models. It's the bridge between experimentation and deployment, letting you stage models, approve them for production, and roll back when things go wrong.

### Basic Experiment Tracking

Let's see MLflow in action. The following example trains a simple classifier and logs everything to MLflow:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# Set the experiment name
# All runs will be grouped under this experiment
mlflow.set_experiment("sentiment-classifier")

# Start a run - this creates a new experiment record
with mlflow.start_run(run_name="random-forest-baseline"):
    # Log parameters - the knobs you can turn
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    mlflow.log_param("dataset_version", "v3.2")
    mlflow.log_param("random_seed", 42)

    # Train the model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate and log metrics - the outcomes you measure
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average='weighted')

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("train_samples", len(X_train))
    mlflow.log_metric("test_samples", len(X_test))

    # Log the model itself - so we can reload it later
    mlflow.sklearn.log_model(model, "model")

    # Log any artifacts - plots, data samples, reports
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("feature_importance.json")

    # Get the run ID for reference
    run_id = mlflow.active_run().info.run_id
    print(f"Run ID: {run_id}")
    print(f"Accuracy: {accuracy:.4f}")
```

Every `log_param`, `log_metric`, and `log_artifact` call writes to MLflow's storage. After the experiment finishes, you can browse to the MLflow UI, search for runs with specific parameters, compare metrics across runs, and download the exact model that achieved the best results.

The power becomes apparent when you've run hundreds of experiments. Instead of sifting through folders and notebooks, you query: "Show me all runs with learning_rate < 0.01 and accuracy > 0.9, sorted by F1 score." MLflow returns the exact runs, with everything you need to reproduce them.

### Autologging: Tracking Without Code Changes

Manually logging every parameter is tedious. MLflow's autologging feature automatically captures parameters and metrics for supported frameworks:

```python
import mlflow

# Enable autologging for PyTorch
mlflow.pytorch.autolog()

# Now training automatically logs:
# - Model architecture
# - Optimizer settings (lr, momentum, weight_decay)
# - Loss curves (step by step)
# - Validation metrics
# - Model checkpoints
# - Training time

# Your training code remains unchanged
trainer = Trainer(model, train_loader, val_loader)
trainer.train(epochs=10)
```

Autologging supports several major ML libraries and can capture much of the common training metadata with minimal code changes.

Think of autologging like a security camera that automatically records. You don't have to remember to press "record"—for supported libraries, it's often on by default, capturing most of the important details. You only add manual logging for custom metrics or domain-specific parameters that the framework doesn't know about.

**Did You Know?** Open-source ML tooling can spread quickly because teams can inspect it, adopt it across different environments, and contribute improvements back to a shared ecosystem.

### The Model Registry: From Experiment to Production

Training a good model is only half the battle. Getting that model safely into production—and managing it once it's there—requires a different set of tools. That's what the Model Registry provides.

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# After a successful training run, register the model
model_uri = f"runs:/{run_id}/model"
registered_model = mlflow.register_model(
    model_uri,
    "SentimentClassifier"  # The model's name in the registry
)

# Add documentation - your future self will thank you
client.update_model_version(
    name="SentimentClassifier",
    version=registered_model.version,
    description="""
    BERT-based sentiment classifier trained on v3.2 dataset.
    Achieves 94.2% accuracy on test set.
    Uses 6-layer DistilBERT for efficiency.
    Trained by ML Team, reviewed by Alice.
    """
)

# Transition through lifecycle stages
# Stage 1: None → Staging (for testing)
client.transition_model_version_stage(
    name="SentimentClassifier",
    version=registered_model.version,
    stage="Staging"
)

# After testing passes...
# Stage 2: Staging → Production (live serving)
client.transition_model_version_stage(
    name="SentimentClassifier",
    version=registered_model.version,
    stage="Production"
)
```

The Registry provides four stages: [None (just registered), Staging (under testing), Production (serving live traffic), and Archived (retired)](https://github.com/mlflow/mlflow/issues/10336). Models flow through these stages as they're validated and deployed.

This might seem like bureaucracy, but it prevents disasters. When Sarah's team had the model in a "USE_THIS_ONE" folder, there was no process, no audit trail, no way to know what was actually in production. With the Registry, there's exactly one "Production" version of each model, and you can see exactly when it was promoted and by whom.

### Loading Models from the Registry

Once models are in the Registry, loading them is simple:

```python
import mlflow.pyfunc

# Load the current production model
model = mlflow.pyfunc.load_model(
    model_uri="models:/SentimentClassifier/Production"
)

# Or load a specific version for comparison
model_v2 = mlflow.pyfunc.load_model(
    model_uri="models:/SentimentClassifier/2"
)

# Inference works the same regardless of which framework trained it
predictions = model.predict(input_data)
```

The `models:/` URI scheme is powerful. You can reference by stage ("Production", "Staging") or by version number. Your serving infrastructure can always point at "Production," and the Registry handles which specific version that means.

---

## 2. Weights & Biases: Visualization and Collaboration

### A Different Philosophy

Weights & Biases (W&B) takes a different approach than MLflow. While MLflow emphasizes self-hosting and lifecycle management, W&B emphasizes real-time visualization and team collaboration.

**Lukas Biewald**, W&B's founder, came to ML from a different angle. He had previously founded CrowdFlower (now Figure Eight), a data labeling platform. He saw firsthand how data quality affects model quality. When he started W&B in 2017, his vision was a platform where teams could see their experiments in real-time, collaborate on interpreting results, and share insights instantly.

W&B emphasizes fast visualization so teams can inspect metrics immediately instead of building custom plotting workflows after training.

The name "Weights & Biases" comes from the fundamental parameters in neural networks—but it's also a nod to the scientific process: we all have biases, and tracking helps us account for them.

**Did You Know?** W&B became popular by focusing on fast experiment visualization, easy sharing, and collaboration features for research teams.

### Basic W&B Logging

W&B's API is deliberately simple. You initialize a run, log what you want, and W&B handles the rest:

```python
import wandb
import torch
import torch.nn as nn

# Initialize a run - this creates a new experiment record
wandb.init(
    project="sentiment-classifier",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "BERT-base",
        "dataset": "sentiment-v3.2",
        "optimizer": "AdamW"
    },
    notes="Testing BERT-base with lower learning rate",
    tags=["bert", "experiment", "v3.2-dataset"]
)

# Training loop with real-time logging
for epoch in range(wandb.config.epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Log metrics - they appear in the dashboard in real-time
        wandb.log({
            "train_loss": loss.item(),
            "epoch": epoch,
            "batch": batch_idx,
            "learning_rate": get_lr(optimizer)
        })

    # Validation at end of each epoch
    val_loss, val_acc = evaluate(model, val_loader)
    wandb.log({
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "epoch": epoch
    })

# Save the trained model as an artifact
artifact = wandb.Artifact("sentiment-model", type="model")
artifact.add_file("model.pt")
wandb.log_artifact(artifact)

wandb.finish()
```

The moment you call `wandb.log()`, the metric appears in the W&B dashboard. If you're training on a remote server, you can watch the training curves update in real-time from your laptop. Multiple team members can compare runs side by side in the dashboard.

### W&B Sweeps: Hyperparameter Optimization

One of W&B's most popular features is Sweeps—built-in hyperparameter optimization. Instead of manually trying different configurations, you define a search space and let W&B explore it:

```python
import wandb

# Define the search space
sweep_config = {
    "method": "bayes",  # Options: bayes, random, grid
    "metric": {
        "name": "val_accuracy",
        "goal": "maximize"
    },
    "parameters": {
        "learning_rate": {
            "min": 0.0001,
            "max": 0.1,
            "distribution": "log_uniform_values"
        },
        "batch_size": {
            "values": [16, 32, 64, 128]
        },
        "hidden_size": {
            "min": 64,
            "max": 512,
            "distribution": "int_uniform"
        },
        "dropout": {
            "min": 0.1,
            "max": 0.5
        }
    },
    "early_terminate": {
        "type": "hyperband",
        "min_iter": 3
    }
}

# Create the sweep
sweep_id = wandb.sweep(sweep_config, project="sentiment-classifier")

# Define the training function
def train():
    wandb.init()

    # Config comes from the sweep
    model = build_model(
        hidden_size=wandb.config.hidden_size,
        dropout=wandb.config.dropout
    )

    for epoch in range(10):
        train_epoch(model, wandb.config.learning_rate, wandb.config.batch_size)
        val_acc = evaluate(model)
        wandb.log({"val_accuracy": val_acc, "epoch": epoch})

# Launch sweep agents - these run the experiments
# count=50 means try 50 different configurations
wandb.agent(sweep_id, train, count=50)
```

The Bayesian optimization in Sweeps is particularly smart. It builds a model of the objective function based on completed runs and uses it to pick the next hyperparameters to try. Instead of randomly sampling (which wastes time on obviously bad configurations), it focuses on promising regions of the search space.

The early termination feature (using Hyperband) makes sweeps even more efficient. If a configuration is performing terribly after 3 epochs, why run it for 100? Hyperband automatically kills unpromising runs and redirects resources to better ones.

### W&B Tables: Data and Prediction Visualization

W&B Tables let you log and visualize structured data—predictions, datasets, and anything else that fits in a table:

```python
import wandb

# Create a table for model predictions
table = wandb.Table(columns=["text", "true_label", "predicted", "confidence"])

for text, true, pred, conf in predictions:
    table.add_data(text, true, pred, conf)

# Log the table - it becomes interactive in the dashboard
wandb.log({"predictions": table})

# Log confusion matrix with a single line
wandb.log({
    "confusion_matrix": wandb.plot.confusion_matrix(
        y_true=y_true,
        preds=y_pred,
        class_names=["negative", "positive"]
    )
})

# Log precision-recall curve
wandb.log({
    "pr_curve": wandb.plot.pr_curve(
        y_true=y_true,
        y_probas=y_probas,
        labels=["negative", "positive"]
    )
})
```

Tables in the W&B dashboard are interactive. You can sort by confidence to find high-confidence errors, filter by label to analyze specific classes, and even build custom queries. For debugging model behavior, this is invaluable—you can see exactly which examples the model gets wrong and why.

---

## 3. MLflow vs W&B: Choosing Your Platform

### The Trade-offs

Both MLflow and W&B are excellent tools, but they emphasize different things:

**MLflow** is open-source, self-hostable, and emphasizes the full ML lifecycle. It's the right choice when:
- You need to self-host for security or compliance reasons
- Model serving and deployment are important
- You want full control over your infrastructure
- You prefer an open-source, self-hosted tool

**W&B** is SaaS-first with superior visualization and collaboration. It's the right choice when:
- You want best-in-class experiment visualization
- Team collaboration is a priority
- You need built-in hyperparameter sweeps
- You prefer a managed service over self-hosting

Many teams use both: W&B for experiment visualization during research, MLflow for model registry and deployment in production. The tools aren't mutually exclusive—they solve overlapping but different problems.

Think of it like the difference between GitHub (collaboration, visualization) and your CI/CD system (deployment, operations). GitHub is great for code review and collaboration; CI/CD is great for automated deployment. Similarly, W&B excels at experiment collaboration, while MLflow excels at model lifecycle management.

**Did You Know?** The MLflow vs W&B debate is reminiscent of the MySQL vs PostgreSQL debates of the 2000s. Both are good, both have passionate advocates, and the "right" choice depends on your specific needs. What matters most is that you use SOMETHING—the worst experiment tracking platform is the one you don't use at all.

---

## 4. Experiment Organization Best Practices

### Naming Conventions That Scale

As your experiments grow from tens to thousands, organization becomes critical. Here's a structure that scales:

```
Project: sentiment-classifier
├── Experiment: baseline-models
│   ├── Run: logistic-regression-v1
│   ├── Run: random-forest-v1
│   └── Run: naive-bayes-v1
│
├── Experiment: transformer-experiments
│   ├── Run: bert-base-lr001
│   ├── Run: bert-base-lr0001
│   ├── Run: bert-large-frozen
│   └── Run: distilbert-finetuned
│
├── Experiment: hyperparameter-sweep-2024-01
│   ├── Run: sweep-001 through sweep-100
│   └── (100 runs with different configs)
│
└── Experiment: production-candidates
    ├── Run: candidate-v1.0-validated
    ├── Run: candidate-v1.1-validated
    └── Run: candidate-v1.2-A/B-testing
```

The key is consistency. Every team member should use the same naming conventions, the same experiment groupings, and the same tagging strategy.

### Strategic Tagging

Tags are the secret weapon of experiment organization. A good tagging strategy makes it easy to find any experiment months later:

```python
mlflow.set_tags({
    # Experiment classification
    "experiment_type": "hyperparameter_search",
    "team": "nlp",
    "owner": "alice@company.com",

    # Data provenance
    "dataset_version": "v3.2",
    "dataset_source": "production_logs",
    "data_split": "stratified_5_fold",
    "train_samples": "50000",
    "test_samples": "10000",

    # Model architecture
    "model_family": "transformer",
    "model_base": "bert-base-uncased",
    "model_size_mb": "400",
    "trainable_params": "110M",

    # Training environment
    "gpu": "A100-40GB",
    "framework": "pytorch-2.0",
    "cuda_version": "11.8",

    # Business context
    "project": "customer-sentiment",
    "use_case": "support-automation",
    "priority": "high",

    # Status
    "validated": "true",
    "production_candidate": "true"
})
```

With this tagging, you can query: "Show me all production candidates from the NLP team that were trained on dataset v3.2 using A100 GPUs." The answer comes back instantly.

### Metric Logging Strategy

Not all metrics are equal. Some should be logged at every step; others only once. Here's a framework:

```python
# Step-level metrics: logged frequently during training
for step, batch in enumerate(train_loader):
    loss = train_step(batch)

    # Log every N steps to avoid overwhelming storage
    if step % 10 == 0:
        mlflow.log_metric("train_loss", loss, step=step)
        mlflow.log_metric("learning_rate", get_lr(optimizer), step=step)

# Epoch-level metrics: logged once per epoch
for epoch in range(num_epochs):
    train_metrics = train_epoch()
    val_metrics = evaluate()

    mlflow.log_metrics({
        "epoch_train_loss": train_metrics["loss"],
        "epoch_train_accuracy": train_metrics["accuracy"],
        "epoch_val_loss": val_metrics["loss"],
        "epoch_val_accuracy": val_metrics["accuracy"],
    }, step=epoch)

# Final metrics: logged once at the end
mlflow.log_metrics({
    "best_val_accuracy": best_accuracy,
    "final_test_accuracy": test_accuracy,
    "total_training_time_hours": training_time / 3600,
    "final_model_size_mb": get_model_size(model),
    "total_epochs_trained": actual_epochs,
    "early_stopped": was_early_stopped
})
```

The step-level metrics let you diagnose training dynamics. The epoch-level metrics are for comparing runs. The final metrics are for quick filtering and model selection.

---

## 5. The MLOps Maturity Model

### Understanding Where You Are

Industry maturity models often frame MLOps as a progression from manual experimentation toward stronger automation in training, deployment, and monitoring.

**Level 0: No MLOps** - This is Sarah's team from our opening story. Models live in notebooks. Deployment is manual. There's no version control for models, no experiment tracking, no reproducibility. Surprisingly, a 2021 survey found that 60% of organizations were still at this level.

Early-stage teams often have source control and CI/CD for code but still manage experiments, data versions, and model versions manually.

**Level 2: Automated Training** - This is where MLflow and W&B come in. Experiments are tracked. Models are versioned. There are automated training pipelines. But deployment is still manual—someone has to look at the metrics and decide to deploy.

More mature teams automate model delivery, validation, and safer rollout patterns such as staged releases.

At the most advanced end of the spectrum, teams combine automated retraining triggers, monitoring, alerts, and consistent feature management.

Most organizations should aim for Level 2 as a first milestone. It's achievable with a small team, provides massive benefits, and creates the foundation for higher levels.

**Did You Know?** Even partial improvements in tracking, versioning, and reproducibility can materially reduce operational friction before a team reaches highly automated MLOps.

---

## 6. Production Experiment Tracking Setup

### MLflow Production Architecture

For production use, MLflow needs proper infrastructure: a database for metadata, object storage for artifacts, and authentication for security.

```yaml
# docker-compose.yml for production MLflow
version: '3.8'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.8.0
    ports:
      - "5000:5000"
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://user:pass@postgres:5432/mlflow
      - MLFLOW_ARTIFACT_ROOT=s3://mlflow-artifacts/
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri postgresql://user:pass@postgres:5432/mlflow
      --default-artifact-root s3://mlflow-artifacts/

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

In production, teams typically back MLflow with a database, external artifact storage, and an authentication layer.

### Configuring Clients

Once the server is running, configure clients to use it:

```python
import mlflow
import os

# Point to the tracking server
mlflow.set_tracking_uri("http://mlflow-server.internal:5000")

# Or via environment variables
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server.internal:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"  # If using MinIO

# Now all logging goes to the server, not local files
with mlflow.start_run():
    mlflow.log_param("model", "bert-base")
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "model")
```

Every team member, every training server, and every notebook can point to the same tracking server. Experiments from all sources appear in the same UI, making collaboration seamless.

---

## Hands-On Exercises

### Exercise 1: Set Up Local MLflow Tracking

Start with local tracking to understand the concepts:

```bash
# Install MLflow
pip install mlflow

# Start local tracking server
mlflow server --host 0.0.0.0 --port 5000

# In another terminal, run an experiment
python -c "
import mlflow
mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment('my-first-experiment')
with mlflow.start_run():
    mlflow.log_param('learning_rate', 0.001)
    mlflow.log_metric('accuracy', 0.95)
    print('Run logged successfully!')
"
```

Then browse to http://localhost:5000 to see your experiment.

### Exercise 2: Create a W&B Experiment

Set up W&B and log a training run:

```bash
# Install and login
pip install wandb
wandb login  # Follow the prompts to get your API key

# Run a simple experiment
python -c "
import wandb
import random

wandb.init(project='my-first-project')
for step in range(100):
    wandb.log({'loss': random.random(), 'step': step})
wandb.finish()
"
```

The URL printed at the end takes you to your interactive dashboard.

### Exercise 3: Implement a Full Model Registry Workflow

Practice the complete lifecycle:

```python
import mlflow
from mlflow.tracking import MlflowClient

# Train and log a model (assuming you have X_train, y_train, etc.)
from sklearn.ensemble import RandomForestClassifier

mlflow.set_experiment("model-registry-demo")

with mlflow.start_run() as run:
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")

    run_id = run.info.run_id

# Register the model
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "DemoClassifier")

# Transition through stages
client = MlflowClient()
client.transition_model_version_stage("DemoClassifier", 1, "Staging")
# After testing...
client.transition_model_version_stage("DemoClassifier", 1, "Production")

# Load the production model
production_model = mlflow.pyfunc.load_model("models:/DemoClassifier/Production")
```

---

## Further Reading

### Documentation
- [MLflow Documentation](https://mlflow.org/docs/latest/) - Comprehensive API reference
- [Weights & Biases Docs](https://docs.wandb.ai/) - Guides and tutorials
- [MLflow Model Registry Guide](https://mlflow.org/docs/latest/model-registry.html) - Deep dive on versioning

### Research Papers
- "Hidden Technical Debt in Machine Learning Systems" (Google, 2015) - **D. Sculley** et al.
- "MLOps: Continuous Delivery and Automation Pipelines in Machine Learning" (Google, 2021)
- "Challenges in Deploying Machine Learning" (Paleyes et al., 2022)
- "A Reproducibility Checklist for ML Research" (Pineau et al., 2021)

---

## Key Takeaways

1. **Experiment tracking is not optional** - Without it, ML development degrades into chaos. Every serious ML team uses some form of tracking. The question is whether you use a proper system or a folder called "final_models_USE_THIS_v3."

2. **MLflow is a widely used open-source platform** - It provides experiment tracking, model packaging, and model management workflows that many teams use in self-hosted environments.

3. **W&B excels at visualization and collaboration** - Real-time dashboards, interactive tables, built-in hyperparameter sweeps. A strong experience for teams who want to see their experiments quickly.

4. **The Model Registry bridges experimentation and production** - Staging, Production, Archived—clear lifecycle stages with audit trails. No more "which model.pkl is actually in production?"

5. **Organization scales with discipline** - Consistent naming, strategic tagging, and thoughtful metric logging make the difference between 50 experiments and 5000.

6. **Build automation incrementally** - Start with reliable tracking and reproducibility, then add stronger validation, deployment automation, and monitoring over time.

---

## Did You Know?

**The Hidden Tax of Poor Reproducibility**: Poor reproducibility drains engineering time because teams have to reconstruct old experiments instead of extending reliable, well-documented work.

**The Experiment Explosion**: Large modern ML projects can generate enormous numbers of runs, which makes systematic experiment tracking essential.

**Why "Weights & Biases"?**: Beyond the neural network terminology, the name reflects a philosophy. "Biases" in ML have a specific meaning (the b in y = Wx + b), but they also refer to cognitive biases in researchers. The platform helps you see your data objectively, revealing biases you might not notice otherwise.

---

<!-- v4:generated type=no_quiz model=codex turn=1 -->
## Quiz


**Q1.** Your team retrained a customer support classifier three months after launch, but the new results are worse and nobody can explain why. The old run was trained by a teammate who left, and all you have is a notebook plus a file named `model_final_v3.pkl`. What specific pieces of information should have been tracked to make the original model reproducible, and which MLflow logging calls would have captured them?

<details>
<summary>Answer</summary>
They should have tracked the dataset version, hyperparameters, preprocessing context, random seed, evaluation metrics, and the model artifact itself. In MLflow, that means logging items such as `dataset_version` and `random_seed` with `mlflow.log_param()`, logging outcomes like accuracy and F1 with `mlflow.log_metric()`, and storing the trained model with `mlflow.sklearn.log_model()`. Artifacts such as a confusion matrix or feature importance report should also have been saved with `mlflow.log_artifact()`. The module’s core point is that Git alone tracks code, not the full experimental state needed to reproduce a model later.
</details>

**Q2.** An NLP researcher on your team is iterating quickly in PyTorch and keeps forgetting to manually log optimizer settings, loss curves, and checkpoints. She wants the fewest possible code changes while still capturing most training metadata. What is the best feature to use, and what kinds of information will it record automatically?

<details>
<summary>Answer</summary>
She should use MLflow autologging, such as `mlflow.pytorch.autolog()`. According to the module, autologging automatically captures items like model architecture, optimizer settings, loss curves, validation metrics, model checkpoints, and training time. This is the right choice because it reduces manual logging overhead while still recording the majority of useful experiment metadata.
</details>

**Q3.** Your company has a fraud-detection model that passed offline evaluation, but compliance requires a documented promotion path before anything serves live traffic. You want one clear source of truth for which version is in testing and which version is actually live. How should you use the MLflow Model Registry lifecycle to manage this safely?

<details>
<summary>Answer</summary>
You should register the model after training, then move it through the registry stages from `None` to `Staging`, and only later to `Production` after testing succeeds. The module explains that the Registry provides lifecycle states such as None, Staging, Production, and Archived, with an audit trail for promotions. This avoids the “which file is live?” problem because serving systems can load `models:/ModelName/Production` instead of depending on ambiguous folder names.
</details>

**Q4.** A distributed training job is running overnight on a remote GPU server, and product managers want to watch validation accuracy evolve in real time from their laptops. The team also wants built-in dashboards without writing custom visualization scripts. Which platform is the better fit for this workflow, and why?

<details>
<summary>Answer</summary>
Weights & Biases is the better fit because the module highlights its real-time visualization and collaboration strengths. With `wandb.log()`, metrics appear immediately in the dashboard, so teammates can monitor training live and compare runs without building custom plotting tools. This matches W&B’s SaaS-first philosophy of instant charts, shared dashboards, and collaborative experiment analysis.
</details>

**Q5.** You need to search over learning rate, batch size, hidden size, and dropout for a text classifier, but you do not want to waste compute finishing clearly bad runs. Which W&B capability should you use, and how does it avoid wasting resources?

<details>
<summary>Answer</summary>
You should use W&B Sweeps. The module explains that Sweeps can define a search space and use methods like Bayesian optimization to choose promising hyperparameter configurations instead of sampling blindly. It also supports early termination with Hyperband, which stops poorly performing runs early and shifts compute toward better candidates.
</details>

**Q6.** Six months from now, your platform team wants to answer a query like: “Show all production-candidate transformer runs from the NLP team trained on dataset v3.2 using A100 GPUs.” What experiment organization practice from the module makes this possible?

<details>
<summary>Answer</summary>
A disciplined tagging strategy makes that possible. The module recommends tagging runs with structured metadata such as team, owner, dataset version, model family, model base, GPU type, business use case, and status flags like `production_candidate`. With consistent tags, runs become searchable and comparable instead of disappearing into vague experiment names and folder structures.
</details>

**Q7.** Your organization already uses Git and CI/CD for application code, but model experiments, dataset provenance, and model versions are still managed manually in notebooks and shared folders. Training is repeatable only through individual tribal knowledge. According to the module’s maturity model, what level are you at now, and what is the next practical milestone?

<details>
<summary>Answer</summary>
You are at Level 1: DevOps but not MLOps. The module describes this level as having version control and basic CI/CD for code, while ML-specific concerns like experiment tracking and model versioning remain manual. The next practical milestone is Level 2, where experiments are tracked, models are versioned, and automated training pipelines provide reproducibility.
</details>

<!-- /v4:generated -->
## ⏭️ Next Steps

You now understand experiment tracking and model registry—the foundation of reproducible ML!

**Up Next**: Module 49 - Data Versioning & Feature Stores (DVC, Feast)

---

*Module 48 Complete! You now understand MLflow and Weights & Biases—the tools that transform ML from art to engineering.*

*Remember Sarah's vanishing model: without tracking, you're just one departure away from losing everything you've built. With tracking, every model tells its own story.*

*"What gets measured gets managed. What gets tracked gets reproduced. What gets reproduced gets improved."* — The MLOps Manifesto

## Sources

- [github.com: 10336](https://github.com/mlflow/mlflow/issues/10336) — The MLflow RFC on stage deprecation explicitly lists the four fixed stages and their lifecycle role.
- [MLOps: Continuous Delivery and Automation Pipelines in Machine Learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) — Primary vendor guidance on ML-specific CI/CD/CT patterns and maturity concepts.
- [The MLflow Project Joins Linux Foundation](https://www.linuxfoundation.org/press/press-release/the-mlflow-project-joins-linux-foundation) — Useful background on MLflow's goals, open-source governance, and lifecycle focus.
- [MLflow GitHub Repository](https://github.com/mlflow/mlflow) — Canonical upstream entry point for the project, releases, and current repository state.
- [ICLR Reproducibility Challenge 2019](https://github.com/reproducibility-challenge/iclr_2019) — Relevant context for the reproducibility concerns discussed in the module.
