package com.phicomm.kidlock.ui;

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
