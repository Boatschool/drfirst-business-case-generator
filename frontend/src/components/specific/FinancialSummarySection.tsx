import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  AttachMoney as MoneyIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { BusinessCaseDetails } from '../../services/agent/AgentService';

interface FinancialSummaryProps {
  currentCaseDetails: BusinessCaseDetails;
}

export const FinancialSummarySection: React.FC<FinancialSummaryProps> = ({
  currentCaseDetails,
}) => {
  const { financial_summary_v1 } = currentCaseDetails;

  if (!financial_summary_v1) {
    return null;
  }

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '$0';
    }
    return `$${value.toLocaleString()}`;
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0.0%';
    }
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Divider sx={{ my: 3 }} />
      
      <Typography
        variant="h5"
        component="h2"
        gutterBottom
        sx={{ display: 'flex', alignItems: 'center', mb: 3 }}
      >
        <AnalyticsIcon sx={{ mr: 1, color: 'primary.main' }} />
        📊 Financial Summary
      </Typography>

      {/* Executive Dashboard */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
            Executive Dashboard
          </Typography>
          
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="error.main" fontWeight="bold">
                  {formatCurrency(financial_summary_v1.total_estimated_cost)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Investment
                </Typography>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="success.main" fontWeight="bold">
                  {formatPercentage(typeof financial_summary_v1.financial_metrics?.primary_roi_percentage === 'number' ? financial_summary_v1.financial_metrics?.primary_roi_percentage : 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Base ROI
                </Typography>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="primary.main" fontWeight="bold">
                  {(typeof financial_summary_v1.financial_metrics?.simple_payback_period_years === 'number' ? financial_summary_v1.financial_metrics.simple_payback_period_years : 0).toFixed(1)} years
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Payback Period
                </Typography>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="warning.main" fontWeight="bold">
                  {formatCurrency(financial_summary_v1.financial_metrics?.primary_net_value || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Net Value
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Multi-Scenario Analysis */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
            Multi-Scenario Analysis
          </Typography>
          
          <TableContainer component={Paper} variant="outlined" sx={{ mt: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Scenario</strong></TableCell>
                  <TableCell align="right"><strong>Value Projection</strong></TableCell>
                  <TableCell align="right"><strong>Net Value</strong></TableCell>
                  <TableCell align="right"><strong>ROI</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Chip label="Conservative" color="warning" size="small" />
                      <Typography variant="body2">Low Estimate</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(financial_summary_v1.value_scenarios?.Low || 0)}
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency((financial_summary_v1.value_scenarios?.Low || 0) - (financial_summary_v1.total_estimated_cost || 0))}
                  </TableCell>
                  <TableCell align="right">
                    {formatPercentage(((financial_summary_v1.value_scenarios?.Low || 0) - (financial_summary_v1.total_estimated_cost || 0)) / (financial_summary_v1.total_estimated_cost || 1))}
                  </TableCell>
                </TableRow>
                <TableRow sx={{ backgroundColor: 'primary.light', opacity: 0.1 }}>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Chip label="Most Likely" color="primary" size="small" />
                      <Typography variant="body2"><strong>Base Estimate</strong></Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    <strong>{formatCurrency(financial_summary_v1.value_scenarios?.Base || 0)}</strong>
                  </TableCell>
                  <TableCell align="right">
                    <strong>{formatCurrency((financial_summary_v1.value_scenarios?.Base || 0) - (financial_summary_v1.total_estimated_cost || 0))}</strong>
                  </TableCell>
                  <TableCell align="right">
                    <strong>{formatPercentage(((financial_summary_v1.value_scenarios?.Base || 0) - (financial_summary_v1.total_estimated_cost || 0)) / (financial_summary_v1.total_estimated_cost || 1))}</strong>
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Chip label="Optimistic" color="success" size="small" />
                      <Typography variant="body2">High Estimate</Typography>
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(financial_summary_v1.value_scenarios?.High || 0)}
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency((financial_summary_v1.value_scenarios?.High || 0) - (financial_summary_v1.total_estimated_cost || 0))}
                  </TableCell>
                  <TableCell align="right">
                    {formatPercentage(((financial_summary_v1.value_scenarios?.High || 0) - (financial_summary_v1.total_estimated_cost || 0)) / (financial_summary_v1.total_estimated_cost || 1))}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Methodology */}
      <Card>
        <CardContent>
          <Typography variant="h6" component="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <MoneyIcon sx={{ mr: 1, color: 'info.main' }} />
            Calculation Methodology
          </Typography>
          
          <Stack spacing={2} sx={{ mt: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Investment Cost:</strong> Total development cost from effort estimates and rate cards
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Net Value:</strong> Value Projection - Investment Cost
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>ROI:</strong> (Net Value / Investment Cost) × 100%
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Payback Period:</strong> Time to recover initial investment based on base scenario
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Break-even Ratio:</strong> Investment Cost / Base Value Projection
              </Typography>
            </Box>
          </Stack>

          <Typography variant="caption" display="block" sx={{ mt: 2, fontStyle: 'italic' }}>
            Generated by: Financial Model Agent • 
            Calculation Date: {new Date().toLocaleDateString()}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}; 