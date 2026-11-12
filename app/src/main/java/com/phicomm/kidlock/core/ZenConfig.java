package com.phicomm.kidlock.core;

import android.content.Context;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class ZenConfig {
    public static class Model {
        public Curfew curfew = new Curfew();
        public Rules rules = new Rules();
    }
    public static class Curfew {
        public boolean enabled = true;
        public String start_time = "21:00";
        public String end_time = "07:00";
    }
    public static class Rules {
        public int default_watch_seconds = 1800; // 30 分钟
        public int default_rest_seconds = 600;   // 10 分钟
        public int reward_seconds_per_quiz = 1800;
    }

    private static Model cachedConfig = null;

    public static Model get(Context context) {
        if (cachedConfig != null) return cachedConfig;
        try {
            File ext = new File("/sdcard/zenscreen_config.json");
            InputStream is = ext.exists() ? new FileInputStream(ext) : context.getAssets().open("config.json");
            cachedConfig = new Gson().fromJson(new InputStreamReader(is, "UTF-8"), Model.class);
        } catch (Exception e) {
            cachedConfig = new Model();
        }
        return cachedConfig;
    }

    // 检查当前时间是否处于夜间免打扰时段
    public static boolean isNightCurfew(Context context) {
        Model cfg = get(context);
        if (!cfg.curfew.enabled) return false;
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("HH:mm", Locale.getDefault());
            String nowStr = sdf.format(new Date());
            Date now = sdf.parse(nowStr);
            Date start = sdf.parse(cfg.curfew.start_time);
            Date end = sdf.parse(cfg.curfew.end_time);

            if (start.after(end)) { // 跨天时段，如 21:00 到 07:00
                return now.after(start) || now.before(end);
            } else {
                return now.after(start) && now.before(end);
            }
        } catch (Exception e) {
            return false;
        }
    }
}
