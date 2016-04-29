import os, fnmatch
import yaml

def validate_yaml_file(filename):
    print "Validating {0}".format(filename)
    try:
        load_yaml = yaml.load(file(filename, 'r'))
    except yaml.YAMLError, err:
        raise ValueError("Invalid YAML file: {0}".format(filename))


def test_yaml():
    # Check YAML files for errors
    for root, dirs, files in os.walk('questions'):
        for filename in fnmatch.filter(files, "*.yml"):
            validate_yaml_file(os.path.join(root, filename))
