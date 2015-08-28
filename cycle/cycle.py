import rx as Rx
from rx import Observable,  Observer
from rx.disposables import CompositeDisposable
from rx.subjects import ReplaySubject
from time import sleep

def make_request_proxies(drivers):
  requestProxies = {}
  for name in drivers.keys():
    requestProxies[name] = ReplaySubject(1)

  return requestProxies

def call_drivers(drivers, requestProxies):
  responses = {}
  for name in drivers.keys():
    responses[name] = drivers[name](requestProxies[name])
  return responses

def attach_dispose_to_requests(requests, replication_subscription):
  if isinstance(requests, Observable):
    requests.enumerable = False,
    requests.value= replication_subscription.dispose()
  return requests

def make_dispose_responses(responses):
  def dispose():
    for name in responses:
      if responses.name and responses[name].dispose.callable():
        responses[name].dispose()
  return dispose

def attach_dispose_to_responses(responses):
  if isinstance(responses, Observable):
    responses.enumerable = False
    responses.value = make_dispose_responses(responses)
  return responses

def log_error(err):
  print("Logging Error",err)

def replicate_many(observables, subjects):

  def create_observer(observer):
    subscription = CompositeDisposable()
    for name in observables.keys():
      if not subjects[name].is_disposed:
        subscription.add(observables[name].subscribe(observer=subjects[name], on_error=log_error))
    observer.on_next(subscription)

    def dispose():
      subscription.dispose()
      for x in subjects:
        if hasattr(subjects, x):
          subjects[x].dispose()

    return dispose

  return Observable.create(create_observer)

def run(main, drivers):
  request_proxies = make_request_proxies(drivers)
  responses = call_drivers(drivers, request_proxies)
  requests = main(responses)
  subscription = replicate_many(requests, request_proxies).subscribe()
  requests_with_dispose = attach_dispose_to_requests(requests, subscription)
  responses_with_dispose = attach_dispose_to_responses(responses)
  return [requests_with_dispose, responses_with_dispose]
