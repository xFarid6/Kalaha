# Training Directives: When to Stop Training

## 📊 Key Metrics to Track

### 1. Evaluation Reward (Most Important)
The **EvalCallback** in `train_v2.py` tracks this automatically:

```python
eval_callback = EvalCallback(
    eval_env,
    eval_freq=25_000 // NUM_ENVS,
    n_eval_episodes=10,
    deterministic=True
)
```

**What to watch:**
- **Reward plateaus**: Performance stops improving
- **Reward decreases**: Model is getting worse (overfitting!)

**Example pattern:**
```
Iteration 5:  Avg Reward = 15.2
Iteration 10: Avg Reward = 22.4  ✓ Improving
Iteration 15: Avg Reward = 28.1  ✓ Still good
Iteration 20: Avg Reward = 28.3  ⚠️ Plateauing
Iteration 25: Avg Reward = 27.8  ❌ STOP! Overfitting
```

---

## 🎯 Performance Benchmarks

### Win Rate Targets vs Minimax

| Opponent | Target Win Rate | Classification |
|----------|----------------|----------------|
| Random | 95%+ | Basic competence |
| Minimax(4) | 85%+ | Good |
| Minimax(6) | 70%+ | Very good |
| Minimax(8) | 55%+ | Excellent |
| Minimax(10) | 50%+ | Near-optimal |
| Minimax(12+) | 45%+ | Superhuman |

---

## 🚨 Signs of Overfitting

### 1. Exploiting Specific Patterns
Agent learns to beat **training opponent** but fails against new strategies.

**Test:** Play against opponents NOT seen during training

### 2. Brittle Policies
Small changes cause huge performance drops.

**Test:** Vary initial seeds, change board size

### 3. Reward Hacking
Agent finds unintended strategies that maximize reward but don't align with good play.

**Example:** Always going for extra turns, ignoring better captures

---

## ✅ When to STOP Training

Stop if **any** of these happen:

1. **Eval reward decreases for 3+ consecutive evaluations**
   - Model is overfitting, revert to previous checkpoint

2. **Eval reward plateaus for 500k+ steps**
   - Model has converged, more training won't help

3. **Win rate vs Minimax(10) > 50%**
   - You've achieved superhuman performance! 🎉

4. **Training becomes unstable**
   - Losses oscillate wildly
   - Agent behavior becomes erratic

---

## 📈 Optimal Training Schedule for Kalaha

| Steps | Expected Performance | Action |
|-------|---------------------|--------|
| 0-500k | Learning basics | Keep training |
| 500k-1M | Beating weak bots | Keep training |
| 1M-1.5M | Competitive with Minimax(6) | Monitor closely |
| 1.5M-2M | Peak performance | Ready to stop |
| 2M+ | Risk of overfitting | Stop if no improvement |

**For Kalaha:** 1.5-2M steps should be sufficient.

---

## 🛠️ Monitoring Tools

### Option 1: TensorBoard (Automated)
```bash
# Terminal 1: Training
python kalaha/ai_training/train_v2.py

# Terminal 2: Monitoring
tensorboard --logdir=logs/
# Open http://localhost:6006
```

**Watch these graphs:**
- `eval/mean_reward`: Should trend up then flatten
- `rollout/ep_rew_mean`: Training performance
- `train/policy_loss`: Should decrease
- `train/value_loss`: Should decrease

### Option 2: Manual Testing
Run evaluation scripts in `model_testing/` folder:

```bash
# Quick benchmark
python model_testing/benchmark_bot.py

# Detailed evaluation
python model_testing/evaluate_all.py

# View results
python model_testing/view_results.py
```

---

## 🎯 Stopping Criteria Checklist

```
[ ] Eval reward hasn't improved in last 300k steps
[ ] Win rate vs Minimax(8) > 55%
[ ] Training loss is stable (not decreasing)
[ ] Model plays intelligently (captures, extra turns)
[ ] No obvious bugs or reward hacking
[ ] Performance tested against multiple opponents
```

**If all checked**: STOP and save as your final model!

---

## 💡 Best Practices

### Checkpointing
`train_v2.py` saves checkpoints every 50k steps:

```bash
ls models/kalaha_v2_*
```

**If training goes bad**, revert:
```bash
cp models/kalaha_v2_1500000_steps.zip models/kalaha_latest.zip
```

### Version Control
Name models by performance:
```
kalaha_v2_winrate60_minimax8.zip
kalaha_v2_best_1.5M_steps.zip
```

### Testing Protocol
1. Train for 100k steps
2. Run `benchmark_bot.py`
3. Check win rate
4. If improving: continue
5. If plateaued 3x: stop

---

## 📊 Expected Results Timeline

### After 500k steps:
- Beats Random: 90%+
- Beats Minimax(4): 60%+
- Plays basic tactics

### After 1M steps:
- Beats Random: 98%+
- Beats Minimax(6): 65%+
- Uses captures and extra turns

### After 1.5M steps:
- Beats Minimax(8): 55%+
- Near-optimal opening play
- Strong endgame

### After 2M+ steps:
- Marginal improvements only
- Risk of overfitting
- Time to stop!

---

## 🔬 Advanced: Elo Rating

Track relative strength:

```python
# After running evaluations
python model_testing/calculate_elo.py
```

**Elo targets:**
- 1000: Random baseline
- 1200: Minimax(4)
- 1400: Minimax(6)
- 1600: Minimax(8)
- 1800+: Superhuman

---

## Summary

**TL;DR for Kalaha:**

1. Monitor `eval/mean_reward` in TensorBoard
2. Stop when reward plateaus for 300k+ steps
3. Verify with win rate tests (>55% vs Minimax(8))
4. Save best checkpoint as final model
5. Don't train past 2.5M steps

Your `EvalCallback` automatically saves the best model to `models/best_model.zip`! 🚀
