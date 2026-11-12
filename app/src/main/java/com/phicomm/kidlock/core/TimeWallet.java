package com.phicomm.kidlock.core;

import android.content.Context;
import com.phicomm.kidlock.util.Prefs;

public class TimeWallet {

    // 存入时间燃料（奖励）
    public static void deposit(Context context, int seconds) {
        int current = Prefs.getWatchSeconds(context);
        Prefs.setWatchSeconds(context, current + seconds);
        Prefs.setState(context, Prefs.STATE_NORMAL);
    }

    // 获取当前可用时间（格式化显示）
    public static String getFormattedBalance(Context context) {
        int sec = Prefs.getWatchSeconds(context);
        int mins = sec / 60;
        return mins + " 分钟";
    }
}
