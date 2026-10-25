"""Local Blueprint/config checks; not a substitute for Render API validation."""
from pathlib import Path
import tomllib
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[2]


class DeploymentTests(unittest.TestCase):
    def test_blueprint_paths_port_plan_and_dependencies(self):
        config=yaml.safe_load((ROOT/'render.yaml').read_text())
        self.assertEqual(len(config['services']),1)
        service=config['services'][0]
        self.assertEqual(service['type'],'web')
        self.assertEqual(service['runtime'],'python')
        self.assertEqual(service['plan'],'free')
        self.assertFalse(service['autoDeploy'])
        project=ROOT/service['rootDir']
        self.assertTrue((project/'app.py').is_file())
        self.assertTrue((project/'ui/steps.py').is_file())
        self.assertTrue((project/'requirements-tested.txt').is_file())
        self.assertIn('requirements-tested.txt',service['buildCommand'])
        self.assertIn('--server.port $PORT',service['startCommand'])
        self.assertIn('--server.address 0.0.0.0',service['startCommand'])
        self.assertEqual(service['healthCheckPath'],'/_stcore/health')
        requirements=(project/'requirements-tested.txt').read_text()
        for package in ['streamlit','plotly','reportlab','python-pptx']:
            self.assertIn(package+'==',requirements)

    def test_offline_config_and_dev_dependencies_separated(self):
        project=ROOT/'smart_campus_navigator'
        config=tomllib.loads((project/'.streamlit/config.toml').read_text())
        self.assertFalse(config['browser']['gatherUsageStats'])
        self.assertTrue(config['server']['headless'])
        self.assertNotIn('playwright',(project/'requirements.txt').read_text().lower())
        self.assertIn('playwright',(project/'requirements-dev.txt').read_text().lower())


if __name__=='__main__':unittest.main()
