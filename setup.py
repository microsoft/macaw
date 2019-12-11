from setuptools import setup

setup(
    name='macaw',
    version='0.1',
    packages=['macaw', 'macaw.core', 'macaw.core.mrc', 'macaw.core.retrieval', 'macaw.core.input_handler',
              'macaw.core.output_handler', 'macaw.core.interaction_handler', 'macaw.util', 'macaw.interface'],
    url='https://github.com/microsoft/macaw/',
    license='MIT',
    author='Hamed Zamani',
    author_email='hazamani@microsoft.com',
    description='An extensible conversational information seeking system'
)
