#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_example.cdk_example_stack import FlaskSqsAppStack



app = cdk.App()
FlaskSqsAppStack(app, "CdkExampleNewStack")
app.synth()
