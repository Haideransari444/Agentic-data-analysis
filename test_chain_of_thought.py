#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Chain-of-Thought Report Generation
Real data, real analysis, real insights
"""

from agents.supabase_agent import SupabaseAgent
from data_driven_report import DataDrivenReportGenerator

print("="*80)
print("TESTING CHAIN-OF-THOUGHT REPORT GENERATION")
print("="*80)

# Initialize
print("\n1. Connecting to Supabase...")
supabase_agent = SupabaseAgent()

print("\n2. Initializing Data-Driven Report Generator...")
report_gen = DataDrivenReportGenerator(supabase_agent=supabase_agent)

print("\n3. Generating Report: 'Show me sales by city with trends and patterns'")
print("="*80)

try:
    report_path = report_gen.create_pdf_report("Show me sales by city with trends and patterns")
    
    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print(f"Report: {report_path}")
    print("="*80)
    
    # Open the PDF
    import os
    os.startfile(report_path)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
