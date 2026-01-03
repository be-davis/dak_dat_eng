#!/bin/bash

# FBI Article Text Extraction Script with Auto-Resume
# This script runs the FBI text extractor and automatically restarts it after 45 seconds

echo "🚀 Starting FBI Article Text Extraction with Auto-Resume"
echo "📋 Configuration:"
echo "   - Input file: data/fbi_article_links_combined_20260102_170044.csv"
echo "   - Max articles per run: 10"
echo "   - Restart delay: 45 seconds"
echo "   - Press Ctrl+C to stop the loop"
echo ""

# Counter to track runs
run_count=1

while true; do
    echo "=================================================="
    echo "🔄 Run #${run_count} - $(date)"
    echo "=================================================="
    
    # Run the Python script
    python fbi_extract_text.py --input_file data/fbi_article_links_combined_20260102_170044.csv --max_articles 10
    
    # Check if the script was interrupted by user (Ctrl+C)
    if [ $? -eq 130 ]; then
        echo ""
        echo "⚠️  Script interrupted by user (Ctrl+C)"
        echo "👋 Exiting auto-resume loop"
        break
    fi
    
    # Check if the script completed successfully or was terminated due to bot protection
    exit_code=$?
    
    echo ""
    echo "📊 Run #${run_count} completed with exit code: ${exit_code}"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Run completed successfully"
    else
        echo "⚠️  Run terminated (likely due to bot protection or error)"
    fi
    
    echo "⏳ Waiting 45 seconds before next run..."
    echo "💡 Press Ctrl+C during this wait to stop the loop"
    
    # Wait 45 seconds with a countdown and the ability to interrupt
    for i in {45..1}; do
        echo -ne "   Restarting in ${i} seconds...\r"
        sleep 1
    done
    
    echo ""
    echo ""
    
    # Increment run counter
    ((run_count++))
done

echo ""
echo "🏁 Auto-resume loop ended"
echo "📊 Total runs completed: $((run_count - 1))"
echo "👋 Goodbye!"