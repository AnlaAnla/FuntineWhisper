import time

text = [1,2,3,4,5,6,7]
for t in text:
    text = f"文本: "
    print(f"\r文本: {t}", end="")
    time.sleep(0.5)

print("\nDone!")