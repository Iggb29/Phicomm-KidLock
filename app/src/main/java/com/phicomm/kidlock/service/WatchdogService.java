package com.phicomm.kidlock.service;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;

import com.phicomm.kidlock.core.ZenConfig;
import com.phicomm.kidlock.ui.LockActivity;
import com.phicomm.kidlock.util.Prefs;
import com.phicomm.kidlock.util.RootUtils;

public class WatchdogService extends Service {
    private Handler handler;
    private Runnable ticker;

    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler(Looper.getMainLooper());
        ticker = new Runnable() {
            @Override
            public void run() {
                handleTick();
                handler.postDelayed(this, 1000);
            }
        };
        handler.post(ticker);
    }

    private void handleTick() {
        // 核心进化：夜间免打扰时段，看门狗彻底静默休眠，不打扰成年人看电影
        if (ZenConfig.isNightCurfew(this)) {
            return;
        }

        int state = Prefs.getState(this);
        if (state == Prefs.STATE_NORMAL) {
            int watchSec = Prefs.getWatchSeconds(this) - 1;
            if (watchSec <= 0) {
                Prefs.setState(this, Prefs.STATE_RESTING);
                Prefs.setRestSeconds(this, ZenConfig.get(this).rules.default_rest_seconds);
                launchLockActivity();
            } else {
                Prefs.setWatchSeconds(this, watchSec);
            }
        } else if (state == Prefs.STATE_RESTING) {
            int restSec = Prefs.getRestSeconds(this) - 1;
            if (restSec <= 0) {
                Prefs.setState(this, Prefs.STATE_QUIZ);
            } else {
                Prefs.setRestSeconds(this, restSec);
            }
            ensureLockForeground();
        } else if (state == Prefs.STATE_QUIZ) {
            ensureLockForeground();
        }
    }

    private void ensureLockForeground() {
        if (!LockActivity.isForeground) {
            launchLockActivity();
        }
    }

    private void launchLockActivity() {
        Intent intent = new Intent(this, LockActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(intent);
        RootUtils.runCommand("am start -n com.phicomm.kidlock/.ui.LockActivity");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
