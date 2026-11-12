package com.phicomm.kidlock.engine;

import android.content.Context;

public interface IChallengeEngine {
    String getTitle(); // 模块名称，例如：儿童思维挑战、银发八段锦、成人深思
    void onChallengePassed(Context context); // 挑战通过回调
}
