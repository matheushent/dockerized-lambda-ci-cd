#!/usr/bin/env python3

from aws_cdk import core

from stacks.api import ExampleLambdaAPI
from stacks.pipeline import Pipeline
from stacks.base import Base


props = {'namespace': 'example-pipeline'}


app = core.App()

base = Base(app, f"{props['namespace']}-base", props)

api = ExampleLambdaAPI(app, f"{props['namespace']}-lambda", base.outputs)
api.add_dependency(base)

pipeline = Pipeline(app, f"{props['namespace']}-pipeline", api.outputs)
pipeline.add_dependency(base)

app.synth()