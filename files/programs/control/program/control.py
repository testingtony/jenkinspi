import yaml
import os
import time


def main(control_file="../config/info.yml"):
    while True:
        with open(control_file) as fp:
            config = yaml.load(fp)

        if config['control']['status'] == 'reboot':
            config['control']['status'] = 'runnning'
            with open(control_file, 'w') as fp:
                yaml.dump(config, fp, default_flow_style='', line_break='\r\n')
            os.system('shutdown -r now')

        time.sleep(10)


if __name__ == '__main__':
    main()
