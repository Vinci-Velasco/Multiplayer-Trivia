# code from @exrhizo to support streamlit script-rerun from another thread (needed for client multithreading)
import asyncio
import threading
import gc
from streamlit.runtime.app_session import AppSession
from streamlit.runtime import Runtime
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

def get_browser_session_id() -> str:
   # Get the session_id for the current running script 
    try:
        ctx = get_script_run_ctx()
        return ctx.session_id
    except Exception as e:
        return None
        # raise Exception("Could not get browser session id") from e
        
def find_streamlit_main_loop() -> asyncio.BaseEventLoop:
    loops = []
    for obj in gc.get_objects():
        try:
            if isinstance(obj, asyncio.BaseEventLoop):
                loops.append(obj)
        except ReferenceError:
            ...
        
    main_thread = next((t for t in threading.enumerate() if t.name == 'MainThread'), None)
    if main_thread is None:
        # raise Exception("No main thread")
        print("No main thread, st_notifier.py")
        return None
    main_loop = next((lp for lp in loops if lp._thread_id == main_thread.ident), None) # type: ignore
    if main_loop is None:
        # raise Exception("No event loop on 'MainThread'")
        print("No event loop, st_notifier.py")
        return None
    
    return main_loop
    
def get_streamlit_session(session_id: str) -> AppSession:
    runtime: Runtime = Runtime.instance()
    session = next((
        s.session
        for s in runtime._session_mgr.list_sessions()
        if s.session.id == session_id
    ), None)
    if session is None:
        # raise Exception(f"Streamlit session not found for {session_id}")
        return None
    return session

# This is it!
# get_browser_session_id needs to be run on the relevant script thread,
# then you can call the rest of this on other threads.
streamlit_loop = find_streamlit_main_loop()
streamlit_session = get_streamlit_session(get_browser_session_id())

def notify() -> None:
    # this didn't work when I passed it in directly, I didn't really think too much about why not
    streamlit_session._handle_rerun_script_request()

# This can be called on any thread you want.
# streamlit_loop.call_soon_threadsafe(notify)