package com.phicomm.kidlock.util;

import android.content.Context;
import android.content.SharedPreferences;

public class Prefs {
    private static final String PREF_NAME = "kid_lock_pref";
    public static final int STATE_NORMAL = 0;
    public static final int STATE_RESTING = 1;
    public static final int STATE_QUIZ = 2;

    public static final int DEFAULT_WATCH_SECONDS = 30 * 60;
    public static final int DEFAULT_REST_SECONDS = 10 * 60;

    public static SharedPreferences get(Context context) {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public static int getWatchSeconds(Context context) {
        return get(context).getInt("watch_sec", DEFAULT_WATCH_SECONDS);
    }

    public static void setWatchSeconds(Context context, int sec) {
        get(context).edit().putInt("watch_sec", sec).commit();
    }

    public static int getRestSeconds(Context context) {
        return get(context).getInt("rest_sec", DEFAULT_REST_SECONDS);
    }

    public static void setRestSeconds(Context context, int sec) {
        get(context).edit().putInt("rest_sec", sec).commit();
    }

    public static int getState(Context context) {
        return get(context).getInt("lock_state", STATE_NORMAL);
    }

    public static void setState(Context context, int state) {
        get(context).edit().putInt("lock_state", state).commit();
    }
}
