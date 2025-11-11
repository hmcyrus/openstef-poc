"""
Test script for forecast_from_mulitple_models method
"""
import asyncio
import json
from services.model_service import ModelService
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_forecast_multiple_models():
    """Test the forecast_from_mulitple_models method"""
    
    # Get available trained models
    print("Fetching available trained models...")
    available_models = ModelService.get_trained_models()
    print(f"Available models: {available_models}")
    
    if len(available_models) == 0:
        print("No trained models found. Please train at least one model first.")
        return
    
    # Use the first 2 models if available, otherwise use what's available
    test_models = available_models[:min(2, len(available_models))]
    print(f"\nTesting with models: {test_models}")
    
    # Define the test date (adjust based on your data)
    test_date = "2024-01-15"  # Change this to a date that exists in your data
    print(f"Test date: {test_date}")
    
    # Call the forecast_from_mulitple_models method
    print("\nGenerating forecasts for 24 hours from multiple models...")
    try:
        result = await ModelService.forecast_from_mulitple_models(
            custom_names=test_models,
            date=test_date
        )
        
        # Pretty print the result
        print("\n" + "="*80)
        print("FORECAST RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2))
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total models: {len(result['all_forecasts'])}")
        for model_data in result['all_forecasts']:
            print(f"\nModel: {model_data['custom_name']}")
            print(f"  Number of forecasts: {len(model_data['model_forecasts'])}")
            if len(model_data['model_forecasts']) > 0:
                first_forecast = model_data['model_forecasts'][0]
                last_forecast = model_data['model_forecasts'][-1]
                print(f"  First timestamp: {first_forecast['timestamp']}")
                print(f"  First forecast: {first_forecast['forecast']:.2f}")
                print(f"  Last timestamp: {last_forecast['timestamp']}")
                print(f"  Last forecast: {last_forecast['forecast']:.2f}")
        
        print("\n" + "="*80)
        print("Test completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\nError during forecast: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting forecast_from_mulitple_models test...\n")
    asyncio.run(test_forecast_multiple_models())
