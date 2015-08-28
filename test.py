import cycle
import rx

def log(msg):
  print(msg)

def main(responses):
  responses["dumbDriver"].subscribe(on_next=log)
  obs = rx.Observable.interval(1000)

  return {
    "dumbDriver": obs
  }

def dumbDriver():

  def driver(responses):
    responses.subscribe(on_next=log)
    obs = rx.Observable.interval(200).map(lambda x: x*x)
    return obs

  return driver

drivers = {
  "dumbDriver": dumbDriver()
}

cycle.run(main, drivers)
