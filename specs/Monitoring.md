# Monitoring Specification & Alert Thresholds — LFP Age Classifier

## 1. Service Health
| Signal            | Metric                          | Warning Threshold | Critical Threshold | Action on Trigger | Owner |
|-------------------|----------------------------------|-------------------|-------------------|-------------------|-------|
| Latency           | p95 inference latency (ms)       | >25ms for 5 min   | >30ms for 2 min   | Auto-scale or `make rollback` | ML Engineer |
| Error Rate        | HTTP 5xx / prediction failures   | >1% for 5 min     | >3% for 1 min     | Pause canary, `make rollback` | ML Engineer |
| Throughput        | Requests per second              | <80% of expected  | <50% of expected  | Check upstream load balancer | Infra Engineer |
| Memory            | RAM usage (MB)                   | >80% of limit     | >95% of limit     | Restart container, investigate | Infra Engineer |

## 2. Data Drift Signals
| Signal            | Method                          | Warning Threshold | Critical Threshold | Action on Trigger | Owner |
|-------------------|----------------------------------|-------------------|-------------------|-------------------|-------|
| Input Drift       | PSI on signal distribution       | PSI > 0.05        | PSI > 0.1         | Investigate new data source; schedule retraining | Data Scientist |
| Golden Set Integrity | % of golden set with missing values | >1%            | >5%               | Block release, re-run `make data-check` | Data Scientist |

## 3. Model Quality Proxies
| Signal            | Proxy Metric                     | Warning Threshold | Critical Threshold | Action on Trigger | Owner |
|-------------------|----------------------------------|-------------------|-------------------|-------------------|-------|
| Accuracy Proxy    | Accuracy on golden set (daily)   | <0.85             | <0.80             | Run `make eval-gate`, if fail → `make rollback` | ML Engineer |
| Confidence Stability | Average prediction entropy    | >0.6              | >0.8              | Investigate concept drift; retrain | ML Engineer |

## 4. Cost & Resource
| Signal            | Metric                          | Warning Threshold | Critical Threshold | Action on Trigger | Owner |
|-------------------|----------------------------------|-------------------|-------------------|-------------------|-------|
| Cost per Request  | Average cost per inference ($)   | >0.01             | >0.02             | Optimize model or switch to cheaper tier | FinOps |
| Daily Budget      | Cumulative cost for the day      | >80% of budget    | >100% of budget   | Enable degradation mode (use fallback model) | FinOps |

## Alert Routing
- All **critical** alerts trigger notification to the owner (pager/email).
- All **warning** alerts are logged to #alerts channel and reviewed during daily standup.