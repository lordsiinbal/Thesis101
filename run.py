
import sys
sys.path.insert(0,'./')



from app.__init__ import create_app


if __name__ == '__main__':
    create_app().run(debug=True)
