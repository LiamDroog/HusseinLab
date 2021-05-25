from ControlHub import ControlHub


def main():
    try:
        console = ControlHub()
        console.start()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
