sweeps
======

Very simple way to run arbitrary tasks that need to be audited and retriable.


Included is a sample app that pretends to send surveys to recipients. This is the perfect app for this library: Sending survey emails is a common action taken for an arbitrary number of recipients. It's important all the right recipients receive the message, and that none receive any message more than once. It's also nice to know that each recipient was sent the message. Sweeps handles all those things!

Run the example to see a fully functional implementation in action!

 - All surveys are sent to all recipients exactly once.
 - The sweeps library provides a record of who received what when.
 - The complete implementation is very short.

To run:

   Run
    
    export SWEEP_TASK_LIBS=sweeps.example
    python example.py --setup
    python sweep.py


   and you'll see lots of sent message notices.
   Repeat the run step:
    
    python sweep.py

   and you'll see no messages are sent.
