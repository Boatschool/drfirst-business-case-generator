# Firestore Integration for Automated Evaluation Results

## Overview

The `run_automated_evals.py` script has been enhanced to persist automated evaluation results to Firestore, enabling better tracking of evaluation runs over time and supporting potential evaluation dashboard integration.

## Implementation Details

### Collections Created

1. **`automatedEvaluationResults`** - Individual evaluation results for each golden dataset entry
2. **`automatedEvaluationRuns`** - Summary documents for complete evaluation runs

### Data Structure

#### `automatedEvaluationResults` Collection

Each document represents the result of running one agent against one golden dataset entry:

```json
{
  "eval_run_id": "uuid-string",                    // Links to evaluation run
  "golden_dataset_inputId": "test_prd_001",        // From golden dataset
  "agent_name": "ProductManagerAgent",             // Agent that was tested
  "case_id": null,                                 // May be populated if agent generates case ID
  "trace_id": null,                                // May be populated if logging generates trace ID
  "timestamp": "2025-06-08T13:43:01.786140+00:00", // When result was processed
  "input_payload_summary": "",                     // Summary of input (optional)
  "live_agent_output_summary_or_ref": "",          // Summary or reference to agent output
  "validation_results": {                          // Detailed validation results
    "structural_completeness": false,
    "markdown_validity": true
  },
  "overall_automated_eval_passed": false,          // True if all validations passed
  "agent_run_status": "SUCCESS",                   // SUCCESS or ERROR
  "agent_error_message": "",                       // Error details if agent failed
  "execution_time_ms": 13069,                      // Agent execution time
  "processed_at": "2025-06-08T13:43:01.786102+00:00" // ISO string timestamp
}
```

#### `automatedEvaluationRuns` Collection

Each document represents a complete evaluation run summary:

```json
{
  "eval_run_id": "uuid-string",                    // Unique run identifier
  "run_timestamp_start": "2025-06-08T13:42:48.380358+00:00",
  "run_timestamp_end": "2025-06-08T13:43:02.308021+00:00",
  "total_examples_processed": 2,
  "successful_agent_runs": 2,
  "failed_agent_runs": 0,
  "overall_validation_passed_count": 0,
  "dataset_file_used": "test_golden_datasets.json",
  "success_rate_percentage": 100.0,
  "validation_pass_rate_percentage": 0.0,
  "total_evaluation_time_seconds": 13,
  "agent_specific_statistics": {
    "ProductManagerAgent": {
      "total": 1,
      "successful_runs": 1,
      "validation_passed": 0,
      "avg_execution_time_ms": 13069
    }
  }
}
```

## Key Features

### Error Handling
- Firestore initialization failure doesn't prevent evaluation execution
- Individual save failures are logged but don't stop processing
- Script continues with local file output if Firestore is unavailable

### Correlation Support
- All data includes `eval_run_id` for correlation across collections
- Document IDs use format: `{eval_run_id}_{golden_dataset_inputId}` for individual results
- Run summaries use `eval_run_id` as document ID

### Enhanced Reporting
- JSON and CSV reports now include `eval_run_id` 
- Filenames include `eval_run_id` for easy identification
- Console output shows Firestore persistence status

## Usage

### Running with Firestore Persistence

The script automatically initializes Firestore when run:

```bash
# Standard usage - results saved to Firestore + local files
python run_automated_evals.py --output-format both

# Use custom dataset
python run_automated_evals.py --dataset-path custom_dataset.json

# Custom output filename
python run_automated_evals.py --output-file my_evaluation
```

### Environment Requirements

Ensure your environment has:
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to service account key
- OR Application Default Credentials (ADC) configured
- Firestore API enabled in your GCP project
- Appropriate IAM permissions for Firestore read/write

### Testing

Test Firestore integration:

```bash
# Test basic Firestore connectivity
python test_firestore_integration.py

# Run evaluation with test dataset
python run_automated_evals.py --dataset-path test_golden_datasets.json

# Verify data was saved
python verify_firestore_data.py
```

## Querying Evaluation Data

### Sample Queries

```python
from google.cloud import firestore

db = firestore.Client()

# Get all results for a specific evaluation run
eval_run_id = "your-eval-run-id"
results = db.collection("automatedEvaluationResults").where("eval_run_id", "==", eval_run_id).stream()

# Get results for a specific agent
agent_results = db.collection("automatedEvaluationResults").where("agent_name", "==", "ProductManagerAgent").stream()

# Get only passed validations
passed_results = db.collection("automatedEvaluationResults").where("overall_automated_eval_passed", "==", True).stream()

# Get evaluation run summary
run_summary = db.collection("automatedEvaluationRuns").document(eval_run_id).get()
```

## Monitoring and Maintenance

### Collection Management
- Documents accumulate over time - consider implementing cleanup policies
- Monitor collection sizes and query performance
- Set up Firestore security rules as needed

### Backup Considerations
- Firestore automatic backups handle data protection
- Local JSON/CSV files provide additional backup
- Consider exporting data periodically for long-term archival

## Troubleshooting

### Common Issues

1. **Firestore client initialization failure**
   - Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Verify service account has Firestore permissions
   - Ensure Firestore API is enabled

2. **Permission errors**
   - Service account needs `Cloud Datastore User` or `Firestore Service Agent` role
   - Verify project ID matches between credentials and script

3. **Data not appearing**
   - Check Firestore console directly
   - Run `verify_firestore_data.py` script
   - Look for error messages in script output

### Debug Mode
Enable debug logging to see detailed Firestore operations:

```python
import logging
logging.getLogger('google.cloud.firestore').setLevel(logging.DEBUG)
```

## Future Enhancements

Potential improvements:
- Batch writing for better performance
- Firestore security rules for access control
- Data retention policies
- Integration with evaluation dashboard
- Real-time evaluation monitoring
- Historical trend analysis 