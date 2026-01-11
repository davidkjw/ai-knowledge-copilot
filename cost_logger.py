# cost_logger.py - Cost Tracking and Performance Monitoring
from typing import Dict, Any, Optional
from datetime import datetime
import json
import uuid


class CostLogger:
    """
    Tracks API costs, latency, and usage patterns
    Critical for production monitoring and optimization
    """
    
    # Pricing (example - update with actual pricing)
    PRICING = {
        "claude-sonnet-4": {
            "input": 0.003,   # per 1K tokens
            "output": 0.015   # per 1K tokens
        },
        "claude-opus-4": {
            "input": 0.015,
            "output": 0.075
        },
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        },
        "text-embedding-ada-002": {
            "input": 0.0001,
            "output": 0
        }
    }
    
    def __init__(self, log_file: str = "cost_logs.jsonl"):
        self.log_file = log_file
        self.active_requests = {}
        self.session_stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "latencies": [],
            "errors": 0
        }
        
    def start_request(
        self,
        model: str,
        input_text: str,
        request_type: str = "completion"
    ) -> str:
        """Start tracking a request"""
        request_id = str(uuid.uuid4())
        
        input_tokens = self._estimate_tokens(input_text)
        
        self.active_requests[request_id] = {
            "id": request_id,
            "model": model,
            "request_type": request_type,
            "input_tokens": input_tokens,
            "start_time": datetime.now(),
            "input_text_preview": input_text[:200]
        }
        
        return request_id
    
    def end_request(
        self,
        request_id: str,
        output_text: str,
        success: bool = True,
        error: Optional[str] = None
    ):
        """End tracking a request and calculate costs"""
        if request_id not in self.active_requests:
            return
        
        request_data = self.active_requests[request_id]
        end_time = datetime.now()
        latency = (end_time - request_data["start_time"]).total_seconds()
        
        output_tokens = self._estimate_tokens(output_text)
        
        # Calculate cost
        model = request_data["model"]
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        input_cost = (request_data["input_tokens"] / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Build log entry
        log_entry = {
            "request_id": request_id,
            "timestamp": end_time.isoformat(),
            "model": model,
            "request_type": request_data["request_type"],
            "input_tokens": request_data["input_tokens"],
            "output_tokens": output_tokens,
            "total_tokens": request_data["input_tokens"] + output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "latency_seconds": round(latency, 3),
            "success": success,
            "error": error
        }
        
        # Update session stats
        self.session_stats["total_requests"] += 1
        self.session_stats["total_cost"] += total_cost
        self.session_stats["total_tokens"] += log_entry["total_tokens"]
        self.session_stats["latencies"].append(latency)
        if not success:
            self.session_stats["errors"] += 1
        
        # Write to log file
        self._write_log(log_entry)
        
        # Clean up
        del self.active_requests[request_id]
        
        return log_entry
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count
        Rule of thumb: ~4 chars per token for English
        In production, use tiktoken or similar
        """
        return len(text) // 4
    
    def _write_log(self, entry: Dict[str, Any]):
        """Append log entry to file"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_request_time(self, request_id: str) -> str:
        """Get formatted processing time for active request"""
        if request_id not in self.active_requests:
            return "0.0s"
        
        elapsed = (datetime.now() - self.active_requests[request_id]["start_time"]).total_seconds()
        return f"{elapsed:.1f}s"
    
    def get_total_requests(self) -> int:
        """Get total requests in session"""
        return self.session_stats["total_requests"]
    
    def get_total_cost(self) -> float:
        """Get total cost in session"""
        return round(self.session_stats["total_cost"], 4)
    
    def get_avg_latency(self) -> float:
        """Get average latency in session"""
        if not self.session_stats["latencies"]:
            return 0.0
        return round(sum(self.session_stats["latencies"]) / len(self.session_stats["latencies"]), 3)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        latencies = self.session_stats["latencies"]
        
        return {
            "total_requests": self.session_stats["total_requests"],
            "successful_requests": self.session_stats["total_requests"] - self.session_stats["errors"],
            "failed_requests": self.session_stats["errors"],
            "total_cost_usd": round(self.session_stats["total_cost"], 4),
            "total_tokens": self.session_stats["total_tokens"],
            "avg_latency_seconds": self.get_avg_latency(),
            "min_latency_seconds": round(min(latencies), 3) if latencies else 0,
            "max_latency_seconds": round(max(latencies), 3) if latencies else 0,
            "p95_latency_seconds": round(self._percentile(latencies, 95), 3) if latencies else 0,
            "error_rate": round(self.session_stats["errors"] / max(self.session_stats["total_requests"], 1), 4)
        }
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(idx, len(sorted_data) - 1)]
    
    def analyze_costs(
        self,
        time_window: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze costs over time window
        Useful for budget tracking and optimization
        """
        # Read all logs
        logs = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    logs.append(json.loads(line))
        except FileNotFoundError:
            return {"error": "No logs found"}
        
        if not logs:
            return {"error": "No logs to analyze"}
        
        # Aggregate by model
        by_model = {}
        total_cost = 0
        total_requests = 0
        
        for log in logs:
            model = log["model"]
            if model not in by_model:
                by_model[model] = {
                    "requests": 0,
                    "cost": 0,
                    "tokens": 0,
                    "avg_latency": []
                }
            
            by_model[model]["requests"] += 1
            by_model[model]["cost"] += log["total_cost"]
            by_model[model]["tokens"] += log["total_tokens"]
            by_model[model]["avg_latency"].append(log["latency_seconds"])
            
            total_cost += log["total_cost"]
            total_requests += 1
        
        # Calculate averages
        for model in by_model:
            latencies = by_model[model]["avg_latency"]
            by_model[model]["avg_latency"] = sum(latencies) / len(latencies)
        
        return {
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "cost_by_model": {
                model: {
                    "requests": data["requests"],
                    "total_cost": round(data["cost"], 4),
                    "avg_cost_per_request": round(data["cost"] / data["requests"], 6),
                    "total_tokens": data["tokens"],
                    "avg_latency": round(data["avg_latency"], 3)
                }
                for model, data in by_model.items()
            }
        }
    
    def suggest_optimizations(self) -> Dict[str, Any]:
        """
        Analyze patterns and suggest cost optimizations
        """
        analysis = self.analyze_costs()
        
        if "error" in analysis:
            return {"suggestions": ["Not enough data for optimization suggestions"]}
        
        suggestions = []
        
        # Check if using expensive models unnecessarily
        for model, data in analysis["cost_by_model"].items():
            if "opus" in model.lower() and data["avg_cost_per_request"] > 0.01:
                suggestions.append(
                    f"Consider using Sonnet instead of Opus for {model}. "
                    f"Current avg cost: ${data['avg_cost_per_request']:.4f}/request"
                )
        
        # Check latency issues
        stats = self.get_session_stats()
        if stats["avg_latency_seconds"] > 5:
            suggestions.append(
                f"High average latency ({stats['avg_latency_seconds']}s). "
                "Consider: (1) reducing context size, (2) using streaming, (3) implementing caching"
            )
        
        # Check error rate
        if stats["error_rate"] > 0.05:
            suggestions.append(
                f"Error rate is {stats['error_rate']*100:.1f}%. "
                "Investigate failures and add retry logic."
            )
        
        return {
            "current_costs": analysis,
            "suggestions": suggestions if suggestions else ["System is running efficiently"],
            "potential_savings": self._calculate_potential_savings(analysis)
        }
    
    def _calculate_potential_savings(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate potential cost savings"""
        # Example: If using Opus, estimate savings with Sonnet
        savings = {}
        
        for model, data in analysis.get("cost_by_model", {}).items():
            if "opus" in model.lower():
                # Estimate 80% cost reduction with Sonnet
                potential_saving = data["total_cost"] * 0.8
                savings["model_optimization"] = {
                    "from": model,
                    "to": model.replace("opus", "sonnet"),
                    "estimated_savings": round(potential_saving, 4),
                    "percentage": 80
                }
        
        return savings