import os

# 定义所有文件的相对路径和内容
files = {
    ".github/workflows/build.yml": """name: Build TV Lock APK
on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: 检出源码
        uses: actions/checkout@v4
      - name: 配置 JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - name: 安装 Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.5'
      - name: 编译 Debug APK
        run: gradle assembleDebug --stacktrace
      - name: 上传 APK 安装包
        uses: actions/upload-artifact@v4
        with:
          name: Phicomm-T1-KidLock-APK
          path: app/build/outputs/apk/debug/*.apk
""",
    "settings.gradle": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "PhicommKidLock"
include ':app'
""",
    "build.gradle": """plugins {
    id 'com.android.application' version '8.2.2' apply false
}
""",
    "app/build.gradle": """plugins {
    id 'com.android.application'
}
android {
    namespace 'com.phicomm.kidlock'
    compileSdk 34
    defaultConfig {
        applicationId "com.phicomm.kidlock"
        minSdk 21
        targetSdk 25
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'com.google.code.gson:gson:2.10.1'
}
""",
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <application
        android:allowBackup="true"
        android:icon="@android:drawable/ic_lock_lock"
        android:label="T1防沉迷"
        android:theme="@style/Theme.AppCompat.NoActionBar">
        <activity
            android:name=".ui.MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />
            </intent-filter>
        </activity>
        <activity
            android:name=".ui.LockActivity"
            android:launchMode="singleInstance"
            android:excludeFromRecents="true"
            android:screenOrientation="landscape"
            android:exported="false" />
        <service
            android:name=".service.WatchdogService"
            android:enabled="true"
            android:exported="false" />
        <receiver
            android:name=".receiver.BootReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter android:priority="1000">
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
""",
    "app/src/main/assets/questions.json": """[
  {
    "id": 1,
    "type": "数学巧算",
    "question": "简便计算：125 × 32 = ？",
    "options": ["A. 3000", "B. 4000", "C. 4200", "D. 3600"],
    "answer": 1,
    "tip": "拆分为 125 × 8 × 4 = 1000 × 4 = 4000"
  },
  {
    "id": 2,
    "type": "数学方程",
    "question": "解方程：3x + 15 = 45，x 的值是？",
    "options": ["A. 8", "B. 10", "C. 12", "D. 15"],
    "answer": 1,
    "tip": "3x = 45 - 15 = 30，解得 x = 10"
  },
  {
    "id": 3,
    "type": "数学小数",
    "question": "计算：0.72 ÷ 0.8 = ？",
    "options": ["A. 0.9", "B. 9", "C. 0.09", "D. 90"],
    "answer": 0,
    "tip": "除数和被除数同时扩大 10 倍：7.2 ÷ 8 = 0.9"
  },
  {
    "id": 4,
    "type": "英语音标",
    "question": "单词 'meat' 和 'beef' 中，划线部分常见的共同发音是？",
    "options": ["A. [i:]", "B. [e]", "C. [æ]", "D. [a:]"],
    "answer": 0,
    "tip": "字母组合 ee 和 ea 多数情况下发长元音 [i:]"
  },
  {
    "id": 5,
    "type": "英语拼读",
    "question": "下列单词中，划线字母组合发音与其他三个【不同】的是？",
    "options": ["A. teacher", "B. read", "C. bread", "D. please"],
    "answer": 2,
    "tip": "bread 中 ea 发 [e]，其他三个均发 [i:]"
  },
  {
    "id": 6,
    "type": "英语拼写",
    "question": "拼写表示“海滩”的单词：b _ _ ch （发音 [bi:tʃ]）",
    "options": ["A. ea", "B. ee", "C. ou", "D. ir"],
    "answer": 0,
    "tip": "beach 表示海滩，字母组合为 ea"
  },
  {
    "id": 7,
    "type": "成语填空",
    "question": "成语缺字选择：掩（ ）盗铃",
    "options": ["A. 耳", "B. 目", "C. 尔", "D. 饵"],
    "answer": 0,
    "tip": "指把自己的耳朵捂住去偷铃铛，比喻自欺欺人"
  },
  {
    "id": 8,
    "type": "成语填空",
    "question": "成语缺字选择：画龙点（ ）",
    "options": ["A. 睛", "B. 晴", "C. 晶", "D. 清"],
    "answer": 0,
    "tip": "指画好龙后点上眼睛。注意是目字旁的“睛”"
  },
  {
    "id": 9,
    "type": "成语填空",
    "question": "成语缺字选择：滥（ ）充数",
    "options": ["A. 竽", "B. 芋", "C. 鱼", "D. 于"],
    "answer": 0,
    "tip": "竽是古代竹制吹奏乐器，所以是竹字头"
  }
]
""",
    "app/src/main/res/drawable/btn_tv_selector.xml": """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape>
            <solid android:color="#2E7D32" />
            <stroke android:width="4dp" android:color="#FFD700" />
            <corners android:radius="8dp" />
        </shape>
    </item>
    <item>
        <shape>
            <solid android:color="#1B5E20" />
            <corners android:radius="8dp" />
        </shape>
    </item>
</selector>
""",
    "app/src/main/res/values/colors.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="black_overlay">#E6111A11</color>
    <color name="white">#FFFFFF</color>
    <color name="accent_yellow">#FFD700</color>
</resources>
""",
    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">T1防沉迷</string>
</resources>
""",
    "app/src/main/res/layout/activity_main.xml": """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:orientation="vertical"
    android:background="#121212"
    android:padding="20dp">
    <TextView
        android:id="@+id/tv_status"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textColor="#FFFFFF"
        android:textSize="22sp"
        android:text="正在检查 Root 权限..." />
    <Button
        android:id="@+id/btn_grant"
        android:layout_width="260dp"
        android:layout_height="60dp"
        android:layout_marginTop="30dp"
        android:background="@drawable/btn_tv_selector"
        android:focusable="true"
        android:textColor="#FFFFFF"
        android:textSize="20sp"
        android:text="授权并启动守护" />
</LinearLayout>
""",
    "app/src/main/res/layout/activity_lock.xml": """<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/black_overlay"
    android:padding="40dp">
    <LinearLayout
        android:id="@+id/layout_rest"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:gravity="center"
        android:orientation="vertical"
        android:visibility="gone">
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="👀 眼睛休息时间"
            android:textColor="@color/accent_yellow"
            android:textSize="40sp"
            android:textStyle="bold" />
        <TextView
            android:id="@+id/tv_rest_timer"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="20dp"
            android:text="剩余时间 10:00"
            android:textColor="@color/white"
            android:textSize="32sp" />
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="15dp"
            android:text="眺望远方或走动一下，倒计时结束后开始答题"
            android:textColor="#B0BEC5"
            android:textSize="20sp" />
    </LinearLayout>
    <LinearLayout
        android:id="@+id/layout_quiz"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:gravity="center_horizontal">
        <TextView
            android:id="@+id/tv_quiz_progress"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="答对 3 题解锁（第 1/3 题）"
            android:textColor="@color/accent_yellow"
            android:textSize="24sp" />
        <TextView
            android:id="@+id/tv_question"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="20dp"
            android:gravity="center"
            android:textColor="@color/white"
            android:textSize="32sp"
            android:textStyle="bold" />
        <GridLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="30dp"
            android:columnCount="2"
            android:rowCount="2">
            <Button
                android:id="@+id/btn_opt_0"
                android:layout_width="320dp"
                android:layout_height="70dp"
                android:layout_margin="10dp"
                android:background="@drawable/btn_tv_selector"
                android:focusable="true"
                android:textColor="@color/white"
                android:textSize="22sp" />
            <Button
                android:id="@+id/btn_opt_1"
                android:layout_width="320dp"
                android:layout_height="70dp"
                android:layout_margin="10dp"
                android:background="@drawable/btn_tv_selector"
                android:focusable="true"
                android:textColor="@color/white"
                android:textSize="22sp" />
            <Button
                android:id="@+id/btn_opt_2"
                android:layout_width="320dp"
                android:layout_height="70dp"
                android:layout_margin="10dp"
                android:background="@drawable/btn_tv_selector"
                android:focusable="true"
                android:textColor="@color/white"
                android:textSize="22sp" />
            <Button
                android:id="@+id/btn_opt_3"
                android:layout_width="320dp"
                android:layout_height="70dp"
                android:layout_margin="10dp"
                android:background="@drawable/btn_tv_selector"
                android:focusable="true"
                android:textColor="@color/white"
                android:textSize="22sp" />
        </GridLayout>
        <TextView
            android:id="@+id/tv_tip"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="15dp"
            android:textColor="#FF5252"
            android:textSize="20sp" />
    </LinearLayout>
</RelativeLayout>
""",
    "app/src/main/java/com/phicomm/kidlock/model/Question.java": """package com.phicomm.kidlock.model;

import java.util.List;

public class Question {
    public int id;
    public String type;
    public String question;
    public List<String> options;
    public int answer;
    public String tip;
}
""",
    "app/src/main/java/com/phicomm/kidlock/util/RootUtils.java": """package com.phicomm.kidlock.util;

import java.io.DataOutputStream;

public class RootUtils {
    public static boolean checkRoot() {
        return runCommand("echo 1");
    }

    public static boolean runCommand(String cmd) {
        Process process = null;
        DataOutputStream os = null;
        try {
            process = Runtime.getRuntime().exec("su");
            os = new DataOutputStream(process.getOutputStream());
            os.writeBytes(cmd + "\\n");
            os.writeBytes("exit\\n");
            os.flush();
            process.waitFor();
            return process.exitValue() == 0;
        } catch (Exception e) {
            return false;
        } finally {
            try {
                if (os != null) os.close();
                if (process != null) process.destroy();
            } catch (Exception ignored) {}
        }
    }
}
""",
    "app/src/main/java/com/phicomm/kidlock/util/Prefs.java": """package com.phicomm.kidlock.util;

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
""",
    "app/src/main/java/com/phicomm/kidlock/service/WatchdogService.java": """package com.phicomm.kidlock.service;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;

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
        int state = Prefs.getState(this);

        if (state == Prefs.STATE_NORMAL) {
            int watchSec = Prefs.getWatchSeconds(this) - 1;
            if (watchSec <= 0) {
                Prefs.setState(this, Prefs.STATE_RESTING);
                Prefs.setRestSeconds(this, Prefs.DEFAULT_REST_SECONDS);
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
""",
    "app/src/main/java/com/phicomm/kidlock/receiver/BootReceiver.java": """package com.phicomm.kidlock.receiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import com.phicomm.kidlock.service.WatchdogService;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Intent serviceIntent = new Intent(context, WatchdogService.class);
        context.startService(serviceIntent);
    }
}
""",
    "app/src/main/java/com/phicomm/kidlock/ui/MainActivity.java": """package com.phicomm.kidlock.ui;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.phicomm.kidlock.R;
import com.phicomm.kidlock.service.WatchdogService;
import com.phicomm.kidlock.util.Prefs;
import com.phicomm.kidlock.util.RootUtils;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView tvStatus = findViewById(R.id.tv_status);
        Button btnGrant = findViewById(R.id.btn_grant);

        btnGrant.setOnClickListener(v -> {
            boolean hasRoot = RootUtils.checkRoot();
            if (hasRoot) {
                tvStatus.setText("状态：已获取 Root 权限，守护中！");
                Toast.makeText(this, "Root 授权成功，守护已激活！", Toast.LENGTH_SHORT).show();
                startService(new Intent(this, WatchdogService.class));
            } else {
                tvStatus.setText("状态：未获得 Root 权限，请在弹窗中允许！");
            }
        });
    }
}
""",
    "app/src/main/java/com/phicomm/kidlock/ui/LockActivity.java": """package com.phicomm.kidlock.ui;

import android.app.AlertDialog;
import android.content.res.AssetManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.phicomm.kidlock.R;
import com.phicomm.kidlock.model.Question;
import com.phicomm.kidlock.util.Prefs;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.util.Collections;
import java.util.List;

public class LockActivity extends AppCompatActivity {
    public static boolean isForeground = false;

    private LinearLayout layoutRest, layoutQuiz;
    private TextView tvRestTimer, tvProgress, tvQuestion, tvTip;
    private Button[] btnOptions = new Button[4];

    private List<Question> questionList;
    private Question currentQ;
    private int correctCount = 0;
    private final int TARGET_CORRECT = 3;

    private Handler handler;
    private Runnable uiUpdater;
    private int menuClickCount = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_lock);

        layoutRest = findViewById(R.id.layout_rest);
        layoutQuiz = findViewById(R.id.layout_quiz);
        tvRestTimer = findViewById(R.id.tv_rest_timer);
        tvProgress = findViewById(R.id.tv_quiz_progress);
        tvQuestion = findViewById(R.id.tv_question);
        tvTip = findViewById(R.id.tv_tip);

        btnOptions[0] = findViewById(R.id.btn_opt_0);
        btnOptions[1] = findViewById(R.id.btn_opt_1);
        btnOptions[2] = findViewById(R.id.btn_opt_2);
        btnOptions[3] = findViewById(R.id.btn_opt_3);

        for (int i = 0; i < 4; i++) {
            final int index = i;
            btnOptions[i].setOnClickListener(v -> checkAnswer(index));
        }

        loadQuestions();

        handler = new Handler(Looper.getMainLooper());
        uiUpdater = new Runnable() {
            @Override
            public void run() {
                refreshUI();
                handler.postDelayed(this, 1000);
            }
        };
    }

    private void loadQuestions() {
        try {
            AssetManager am = getAssets();
            InputStream is = am.open("questions.json");
            Type listType = new TypeToken<List<Question>>(){}.getType();
            questionList = new Gson().fromJson(new InputStreamReader(is), listType);
            Collections.shuffle(questionList);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        isForeground = true;
        handler.post(uiUpdater);
    }

    @Override
    protected void onPause() {
        super.onPause();
        isForeground = false;
        handler.removeCallbacks(uiUpdater);
    }

    private void refreshUI() {
        int state = Prefs.getState(this);
        if (state == Prefs.STATE_RESTING) {
            layoutRest.setVisibility(View.VISIBLE);
            layoutQuiz.setVisibility(View.GONE);
            int restSec = Prefs.getRestSeconds(this);
            tvRestTimer.setText(String.format("剩余休息时间 %02d:%02d", restSec / 60, restSec % 60));
        } else if (state == Prefs.STATE_QUIZ) {
            layoutRest.setVisibility(View.GONE);
            layoutQuiz.setVisibility(View.VISIBLE);
            if (currentQ == null) {
                nextQuestion();
            }
        } else {
            finish();
        }
    }

    private void nextQuestion() {
        if (questionList == null || questionList.isEmpty()) return;
        Collections.shuffle(questionList);
        currentQ = questionList.get(0);

        tvProgress.setText(String.format("要求连对 3 题（当前已答对: %d/%d）", correctCount, TARGET_CORRECT));
        tvQuestion.setText(String.format("[%s] %s", currentQ.type, currentQ.question));
        tvTip.setText("");

        for (int i = 0; i < 4; i++) {
            if (i < currentQ.options.size()) {
                btnOptions[i].setText(currentQ.options.get(i));
                btnOptions[i].setVisibility(View.VISIBLE);
                btnOptions[i].setEnabled(true);
            } else {
                btnOptions[i].setVisibility(View.GONE);
            }
        }
        btnOptions[0].requestFocus();
    }

    private void checkAnswer(int selected) {
        if (currentQ == null) return;
        for (Button btn : btnOptions) btn.setEnabled(false); // 禁用按钮防连点

        if (selected == currentQ.answer) {
            correctCount++;
            if (correctCount >= TARGET_CORRECT) {
                Prefs.setState(this, Prefs.STATE_NORMAL);
                Prefs.setWatchSeconds(this, Prefs.DEFAULT_WATCH_SECONDS);
                Toast.makeText(this, "🎉 答题通过！奖励观看 30 分钟！", Toast.LENGTH_LONG).show();
                finish();
            } else {
                Toast.makeText(this, "回答正确，继续加油！", Toast.LENGTH_SHORT).show();
                nextQuestion();
            }
        } else {
            correctCount = 0;
            tvTip.setText("回答错误！解析：" + currentQ.tip);
            btnOptions[0].postDelayed(this::nextQuestion, 3000);
        }
    }

    @Override
    public void onBackPressed() {}

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        if (event.getAction() == KeyEvent.ACTION_DOWN) {
            if (event.getKeyCode() == KeyEvent.KEYCODE_BACK) {
                return true;
            }
            if (event.getKeyCode() == KeyEvent.KEYCODE_MENU) {
                menuClickCount++;
                if (menuClickCount >= 4) {
                    showParentDialog();
                    menuClickCount = 0;
                }
                return true;
            }
        }
        return super.dispatchKeyEvent(event);
    }

    private void showParentDialog() {
        final EditText input = new EditText(this);
        input.setHint("输入家长 PIN 码 (默认 8888)");
        new AlertDialog.Builder(this)
                .setTitle("家长控制通道")
                .setView(input)
                .setPositiveButton("解锁2小时", (dialog, which) -> {
                    if ("8888".equals(input.getText().toString().trim())) {
                        Prefs.setState(this, Prefs.STATE_NORMAL);
                        Prefs.setWatchSeconds(this, 120 * 60);
                        finish();
                    } else {
                        Toast.makeText(this, "密码错误", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton("取消", null)
                .show();
    }
}
"""
}

# 自动建立目录并写出文件
for path, content in files.items():
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ 所有 18 个文件已全部自动生成完成！")