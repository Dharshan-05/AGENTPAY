import fs from 'fs';
import path from 'path';
import https from 'https';

const outputDir = path.resolve('docs/stitch-assets');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const screens = [
  { id: '8c970153e50d4894b25e65b3ce37008b', title: '01-dashboard-overview', img: 'https://lh3.googleusercontent.com/aida/AEtjO1UhL5p7NeKScRUpnh3GOpN_5k0XEkeCqMwqoNkTeQZ2IV1PYFtKVGuCUnLbm3vfczt8H8lSPXBXd-u2ep9dUHl3StuC9MFVQIIegL-nXQcluHn48C6GqBIWC5PFJiA_0LrlzQmJSx8Nw_vqI9A8p9frTb5EQI9vfM3V4weshbRd1yjaWCEUf1c4WWzDbEFmDZxsHoH_L4tDYWKpbn1pmGQREolWyJOXxsQ62HX6h5DeR5_uS_kqeE2EsCI', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NWY3Y2QzNTkwOTI1YzczNzg3MGQ2NGUwEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '48c3ec0ae6104ed498cfd236989bd466', title: '02-secure-login', img: 'https://lh3.googleusercontent.com/aida/AEtjO1UPvpIeFx8zPHiu1qt6-BynJKw7Z591zdfARNcyETjZdzCqtYFfyWou8oG9vwRN-J7HC5T_QzK2Zm0G3xaon7GogzyPFuLA-qTP1n2TZ8r46pP6yLiD3R0pMoSSxfwedbkRMOB7A9OV7YFlTu5bgZttbM1he4QBqZk1DI2w9aQYW-eYomrQCnr_V-qIjUoLFt6azG3mF89yKsbWMAMfApbYQ7Bri8xL7ZgdtF_FABMgoPyIaIuc84-3oYE', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NWRmMGIwMTYwOTI1ZDU5YmFlMDc2Mjc2EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'f6ff1b0dcfa14eb9b293156aa81b32a3', title: '03-ai-command-agent-management', img: 'https://lh3.googleusercontent.com/aida/AEtjO1XhMKDqrJ8niOiOjBcJpYt9Qw1T6IBzx5p-T78gYbYi6CPFRZWVyFMXKMxwYFrhkE4dDROAThZBK4JN9g7X1rt00xg3SJ-kO8NnvGqrvN-XMf9idZaS0U0wLw48vscaQjpgmju9M2Or12QBnbXIwIHKOJksgJO32V36W-UjnCH_nv-eoREW8Q7yegrcCQknzGnRBncjNHZxTkHcL5Sg_L70JU9xMIXq0KSO_evpTOw_h7QBXOu78-oTyhw', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NWYxNjc3NjYwMWE2MDEwYzM2MGIzMzFmEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '659a41316e5b4b8985850e9f515842ca', title: '04-create-account', img: 'https://lh3.googleusercontent.com/aida/AEtjO1VFI7VVZNZrLC0oLab3XyTvv6ceT2dt0DS6LyhSSakL5tsZfZQSIRfQLBNu-glfKUBmeVxuxP15X5jmwoKXxkc0o2JbhwYjEilFRw6yZ6GzphNQlA14HgaFoES0dH0Zb2klD2gl-Hl2avztVBg5jpsm-AcrTNT7CmhDcEx29rHi7QYnPTfiXAjNPoh5B6cSPOyl8ZbcoqTFNlLum7cS-eh8OEgkE2fIE3plLC4NWc3EDMTkuygk25Arjkk', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NmNhNDQ1NjUwMzM4NWM4Nzg2MWJjZjM3EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '71771d0736fc4a86b9302b9b3f1fc508', title: '05-2fa-verification', img: 'https://lh3.googleusercontent.com/aida/AEtjO1WkfabXHBgTJNJSJ22Qnp2FUWNeNKQRfr5vvjy3OP38AmjpfcvzpLJJmTcbF2kjylJ7vFO9DnSSo5bjekWrH0DgKaPfkNQ9aRHt_w6CTGB2r_Ne-yn_5kfNMb0bB1vjkpiKlFpS4xrmg3lFiIYJds9pv82wjjJtCvQP3qIKz2NvrVnorQPOr4FFivQIeKCpuyE51pz8ybiUKmoTUs5ljwsDHGDwgsL86pNynQPoznp8wRHD9FYhbgUKH5I', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NmJiZjRhNGIwNTIyODJmZWI4MDhiZGQ3EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'd88d67ef7b064742981858d43fb0d29c', title: '06-onboarding-security-config', img: 'https://lh3.googleusercontent.com/aida/AEtjO1WFAOaMnAHSRaOfeLo_MnapIokrL8AhSHqWRk-gKwyUReKfYeXfIlRmYdTe-xsqEQp2x76N8SMDOSrRsZThHtWQUfE0yqb1hpiMXhbtzeA9_VLwN5n4AflO_cQXApRCj2wGXTXQ6oByK6dBJ6T9YLAxlDDvj3efNfARa5iKCg7EZ-MlAg7zH8727McwMcSfI9ZmmwZrdM0qPAjFv7VXjPyWwMQQiJTHcPyndGRRkUhiVcJ9tC2LJCob2A', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NmNkNjg5YTUwMWI0ZTc2NzdlMTI3NGM5EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'f9d5818362de451e8446243874caeefb', title: '07-onboarding-system-ready', img: 'https://lh3.googleusercontent.com/aida/AEtjO1V32GjfSVe-B76W00psy5qXB1YPB1xz8QHZ0mfLy_UxQjaqhsyXh_QzpBFR92fcTP9BKIhRbvKJpT9sYzWTt27QQdWoOKX_5OrrhtcWgjzhiWszTymKbTgX7ROhOcGNqE-IMCqFdz7L1LXiXmjy9MwbflZOpac9UXXgJvofGnoDJJRz-_5hHhfoJMwcgYNgbYnyT395-8BVs5FM7Os6ThXL6oPnQuuOIxDr3qUYZ5SgubzfBHUDw0RJUTk', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NmM0YWFmZGIwNTIyYTQzNDFiMjliMmFlEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '37aca24de0e84878a379a0033f684a3f', title: '08-reset-password', img: 'https://lh3.googleusercontent.com/aida/AEtjO1VKVx0_X-HBdJ-zfcFBgquqZfhHA5NNv8hNSpGBqTCWruPc2oWeuEDnf2zuf3LI69l3YGDvDfeTodkWWcxWxzroorcITfdLXelTwYACUbDKzijKQxBuuEKjVJBI5R7pzynmBchGGWAdcHzA3SlMe2Nl_LkJzCqQs2qO4Cif4aX0sQhx4Efkd7OhkjFqkql99yGiFWcpZb6KbJzUQnWwGFyloO8lEs5-F3f6Q162ew4FiWpDU6sG8QNZqDc', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3NmIzMDI4M2QwNDczNmRmMDRkMGZjYTMwEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'e442153bace4423a9fa85374c8a644ef', title: '09-command-center-dashboard', img: 'https://lh3.googleusercontent.com/aida/AEtjO1WXavLJlYPqPtbOM1t0ugOq5Wja2VtsSg4eiUo8Y2Vk7pMLBIQOpZwxm7KLzLUPoyzDl3sZ5E9HsTg7aChrQ4sTH8vXg_fbYzWQucRhhkaNtz6xcsiUFYVskqM_Iw7kb_wZc45XYz3YG2p7KQlh4tEhafVY9_wDLhHQBJmMRl-pJpzx7weKZYuL0q2-L1Pf1GaYR4FfsD4bcwnSWizEn4Oolq_opT1iWdXvg1Z7Nrp4pCE3t2DVuALFa7w', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3N2E1YmJhNTYwODlhZjUxMGQ5MTk2YTczEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '25994890dd194e12a02671c70aa5f717', title: '10-transaction-operations-center', img: 'https://lh3.googleusercontent.com/aida/AEtjO1V2VCXK__4lQCjhwiUAjXIci50e9Yod7BV2dJS8OEpTr5cGUYE6aDfi3pN1oCSt__2Jww4nXW4h78iO39yqSSE3oxROpbwhwB3k5TPQ8slrU00kisMxkVMHXwS0N29XAzTBYoRyeYO74jZ31xvl56CFXvYoBWCphXVOXPH6mANkAQb_NoMIQTd486p98kX1jkqBsthkJVlIAXhI4frViQPeXmBpvy_H_C_wIK5-0HxnEMPJ_BkgsYZRwdg', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3ODBmZWM1MzMwN2M0Y2YwZDA3MmZhZjhmEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '265105a7ee7545619610ab5c306ace3b', title: '11-merchant-details-acme', img: 'https://lh3.googleusercontent.com/aida/AEtjO1VorgMFz9bAeKiO-owPVP4vzM4iOAEPD6rbdbNyfRmyal2r3queCOYXoXlqyUBMkxd2BSPUgr624BUuvqDn-vHkKGToJIr_P_Sj3NRdUHv7UeWwMD3S5CVzinJ-G4-raZFDQy076jD2KepyDVouVlECTnBVSuTbvHEyx99stAfkdxjBFRxBaOMZ90AxHu8I01uDGjsYUSj3rfL_rJ_-msyl9TUrydJ5nhvExa2UYFhMQpv99qwvxo1MLDw', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3YmJhMDZiYmQwMzgzOWVhZjc1MDI2NTQ4EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '112e49239c30462aa4ba88531050765e', title: '12-merchant-management', img: 'https://lh3.googleusercontent.com/aida/AEtjO1X4fB-ApHc3wrOXQtFRzKqs82DF7_rKWGzM6bpb4l7SFQHc6dM4g-FxOWV9fYRNwwAWmtoahOviuiHlxc30v05nHgHEugpFiJxF6VSbU8JBf5V_XAcQkgeYQVzwi_mwxq_tthri5OfjzP-eDBaGHLiUaLuOUIcAC-0dOKz_iJbWTJxU7diG6dQcryI8bN2lz7ScA-9xuwtNh1IjLrEdX834N6tz8bEUUlRncwaAY71nZXBzwsZ9BNwFEA', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3YmJjZWQ1MTgwMWE2MDlkNGU2MTU4YzFmEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '0bb008804e5a4bed860d81c202be918b', title: '13-merchant-onboarding', img: 'https://lh3.googleusercontent.com/aida/AEtjO1W_FaeuUJSAwzyHfeVXUhZhIeT8wkG45RPbHC8eEZD6b2v9otvOBv0VaQnCT5SdcxH7DPcJqgJ1a9rVw4dzXxGCZFaZzShg0MBnXDYNqP5vLLnPB8zO_4FA_jGouIYuQPca5oD9YjMtINy5wQKYaYkKK0ek1XMikSwhezpie75CbWKhjLTK94fTDVEiyC08En6Vd7CGRh-3RPukQM7AQZgCzpfysJL1Tc0kGsmLRHYIKdz6iyXLObsVAhc', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3YmI3YTU2OTMwMzgzOTJhMmRmMDNiNDY4EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'd60474fe72c44ab0b693be5572c6bfe6', title: '14-payments-overview', img: 'https://lh3.googleusercontent.com/aida/AEtjO1UHpXMPG7Ijwspk1dkfTOOwXh4axr1WoS8FeG9Ukc-2XLBb56b2Lp5QA9sg_3QjI50PtszOMla7K-ecVTyHzBfhoNeOPLMQ7depaG_DIDZmsQT7fxwg7SU_H-ZuFhXWFSc7_INSvgWu5zEXqAGj5XVs336S0o2son6-D8sba5ZkxSZxm3jItTPulGV8-_NuIS1G5Gu6yDYy5UTzWveWdoiHPX3q47BSyc9Fx055txZ1GE_WpOlU0LRiFUI', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3Y2ViYjJjZGQwMWI0ZTc2NzdlMTI3NGM5EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: 'ae1bc4a2f0504e74bfcf67b18d6fd956', title: '15-payment-directory', img: 'https://lh3.googleusercontent.com/aida/AEtjO1UuTM9gT18_Sie0O2relfccGVH_i5wbSNTt4ZsLZ87DuOBIvyoyVvdyKKUYHlYLi0vNYCz3G0GK7LdKuZysPuE1KJ0l0ucfYnKreydFaSA-PZdxO9_buT-nRDe3PU8Dh_HIIrQfzaWY6ZICzYltX83q9KLvEmHfj_kBsZYBDYvLXkUqBXhVW9lpfsHfxVnxWEUh3djYXsUmvPu2RLavrnCxTXEva3t6At1yLch4rRRld-buja-EwQFtVT8', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3Y2VlOTQ5NTgwMWE2MGU0YTcyMDQxMTg0EgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' },
  { id: '554d2a588aa84ceebbad0dc169d5d7d3', title: '16-payment-directory-fixed', img: 'https://lh3.googleusercontent.com/aida/AEtjO1Veua2uG4d7HS2mkJbhFWDEx3nM9HvUPc5yvGDz3Cg6_tC49YRI3p-RcXxWbDyN8EX3T3kVoAXshbLxUfAp8gxF34YvBsrzFp5BKmOC-hBkKbvYrknYnyzf_vzGyd0YtRXbH_nspebR2PNYh8XAIS9l9himsbXWvu4eJ9bHOlLE5J9Nm-QrXA4WnBqinWI7Qjq53BgGfPiGpLeePX0FfUNbCZt4dlJvsoxCsGpEbQtI8QNDCS9r3pjg4g', html: 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OWQ3ZGNlMmU2MTEwN2UwMGVlODdmMjIzYjdkEgsSBxDR-YGIhQYYAZIBIwoKcHJvamVjdF9pZBIVQhM5MTgxOTI5NTE4NzM2MzcwNjY3&filename=&opi=89354086' }
];

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        https.get(response.headers.location, (res) => {
          res.pipe(file);
          file.on('finish', () => { file.close(); resolve(); });
        }).on('error', reject);
      } else {
        response.pipe(file);
        file.on('finish', () => { file.close(); resolve(); });
      }
    }).on('error', reject);
  });
}

async function downloadAll() {
  console.log('Downloading 16 Stitch screen assets...');
  for (const s of screens) {
    const imgPath = path.join(outputDir, `${s.title}-screenshot.png`);
    const htmlPath = path.join(outputDir, `${s.title}.html`);
    console.log(`[+] Downloading ${s.title}...`);
    try {
      if (s.img) await downloadFile(s.img, imgPath);
      if (s.html) await downloadFile(s.html, htmlPath);
    } catch (e) {
      console.error(`[-] Error downloading ${s.title}:`, e.message);
    }
  }
  console.log('Finished downloading all 16 screens.');
}

downloadAll();
