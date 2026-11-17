"""Reviewer-only evidence finalization; no candidate, Game, network, engine or controller writes."""
from pathlib import Path
import hashlib,json,math,shutil
Q=Path(__file__).resolve().parent
ROOT=Q.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(n,x):(Q/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assert not (Q/'FINAL_HASHES.json').exists(), 'Final packet already immutable'
manifest=load(Q/'job-manifest.json')
assert sha(Q/'run_signal_job.py')==manifest['entrypoint_sha256']
assert sha(Q/'input-freeze.json')==manifest['input_freeze_sha256']
op='0c23ecf71f324a1c8872cc80ece7bd87'
job=ROOT/'.autopilot/jobs'/op
receipt=load(job/'receipt.json'); inp=load(job/'input.json')
assert receipt['operation']==op and type(receipt['exit_code']) is int and receipt['exit_code']==0
assert receipt['argv_sha256']==inp['argv_sha256'] and sha(job/'output.log')==receipt['log_sha256']
assert inp['cwd']==str(ROOT) and inp['argv'][1]==str(Q/'run_signal_job.py') and inp['timeout']==600
assert Path(inp['argv'][0]).resolve()==Path('/usr/bin/python3').resolve()
copydir=Q/'canonical-job-evidence';copydir.mkdir()
for n in ['input.json','started.json','receipt.json','output.log']:shutil.copyfile(job/n,copydir/n)
statepath=ROOT/'.autopilot/STATE.json';statebytes=statepath.read_bytes();state=json.loads(statebytes)
history=[x for x in state['history'] if x.get('operation')==op]
assert len(history)==1 and history[0]['code']==0
save('canonical-job-evidence/state-history-extract.json',{'source':str(statepath),'source_sha256_at_read':hashlib.sha256(statebytes).hexdigest(),'history':history,'note':'Read-only extract; receipt proves exit0. input.json is immutable initial RUNNING/unconsumed submission, not terminal status. Parent reports consumed; no controller called by QA.'})
result=load(Q/'analysis-01/result.json');raw=load(Q/'independent-raw-recheck.json')
assert result['status']=='PASS_SIGNAL_ONLY' and len(result['asset_checks'])==20
assert all(all(x.values()) for x in result['asset_checks'].values()) and all(result['checks'].values())
assert raw['all20_raw_PCM_metrics_recomputed'] and raw['all20_reproduction_bytes_exact'] and raw['all35_inputs_current_SHA_unchanged']
assets={p.stem:load(p) for p in (Q/'analysis-01').glob('finish_*.json')}
assert len(assets)==20
pairs=load(Q/'analysis-01/profile-comparisons.json')['common_category_crosshero_pairs']
def cos(a,b):return math.fsum(x*y for x,y in zip(a,b))/math.sqrt(math.fsum(x*x for x in a)*math.fsum(x*x for x in b))
recomputed=[]
for p in pairs:
 a,b=assets[p['a']],assets[p['b']]
 fields={
 'time_normalized_envelope_cosine':cos(a['envelope']['time_normalized_RMS64'],b['envelope']['time_normalized_RMS64']),
 'fixed5ms_envelope_cosine':cos(a['envelope']['absolute5ms_RMS64_to320ms'],b['envelope']['absolute5ms_RMS64_to320ms']),
 'logband32_cosine':cos(a['spectrum']['normalized_log_band_power32'],b['spectrum']['normalized_log_band_power32'])}
 for k,v in fields.items():assert abs(v-p[k])<1e-12,(p['a'],p['b'],k)
 recomputed.append({'a':p['a'],'b':p['b'],**fields})
assert len(recomputed)==38
save('independent-pair-recheck.json',{'scope':'Recompute all38 descriptor-pair cosines from actual saved analysis vectors; no listening claim','pairs':recomputed,'all_match_tolerance_1e-12':True})
items=raw['items']
ranges={k:[min(x[k] for x in items),max(x[k] for x in items)] for k in ['RMS_dbfs','sample_peak_dbfs','truepeak8x_dBTP','truepeak_ffmpeg_dBFS','DC','endpoint','tail5ms_RMS_dbfs','internal_silence_seconds','plateau']}
metrics={'scope':'C01_SOURCE_SIGNAL_ONLY','asset_count':20,'catalog_route_counts':{'gabar':3,'olezhka':3,'timka_prime':3,'ryzhik':3,'tega':3,'pasha':5,'timka_present':0},'format':{'sample_rate_Hz':44100,'channels':1,'PCM_bits':16},'duration_seconds':[min(x['duration_seconds'] for x in assets.values()),max(x['duration_seconds'] for x in assets.values())],'ranges':ranges,'total_PCM_rail_samples':sum(x['positive_PCMrails']+x['negative_PCMrails'] for x in assets.values()),'signal_checks':sum(len(x) for x in result['asset_checks'].values()),'catalog_recipe_retention_checks':len(result['checks']),'independent_PCM_recomputed':20,'independent_descriptor_pair_recomputed':38,'byte_exact_recipe_reproduction':20,'input_SHA_unchanged_at_job_and_raw_recheck':35,'legacy_yakuza_WAV_retained':5,'own_oversampling_method':'8x finite32tap-per-phase Lanczos-windowed sinc; numerical estimate, not a certified BS.1770 compliance claim','FFmpeg_method':'ebur128 peak=true, independent decoder exact PCM crosscheck; reported peaks rounded0.1dB','integrated_LUFS':'Informational only for short single shots; not a loudness-target acceptance','no_actual_listening':True,'no_actual_Godot_integration_or_mix':True}
save('metrics.json',metrics)
findings={'scope':'C01_SOURCE_SIGNAL_ONLY','mandatory_signal_findings':[],'listening_priorities':[{'id':'C01-A01','status':'ADVISORY_NOT_LISTENED','topic':'Oleg/Pasha same-category envelope proximity','actual_blunt_envelope_cosine':0.99710361818,'actual_blunt_logband_cosine':0.6824505576,'actual_unarmed_envelope_cosine':0.9954036206,'actual_unarmed_logband_cosine':0.6712944886,'interpretation':'Measured temporal descriptors close while spectral vectors differ. Prioritize comparative listening. No claim of audible sameness or distinctiveness; no mandatory unheard redesign.'}],'remaining_gates':['Actual Godot import/route/cue/playback/once/reset/authority integration','Actual engine/mixer PCM with music/concurrency and clipping/levels/event windows','Artistic listening of sources and actual mix by capable listener'],'profile_similarity_flag_threshold_not_artistic_standard':{'envelope_cosine':0.985,'logband_cosine':0.985,'both_required':True,'flagged_pairs':0}}
save('findings.json',findings)
decision={'schema':1,'scope':'C01_OFFLINE_SOURCE_SIGNAL_ONLY','status':'PASS_SIGNAL_ONLY','reviewer':{'agent':'/root/qa_resume_recovery','role':'INDEPENDENT_QA','authored_audio_candidates':False},'source_binding':{'input_freeze_sha256':sha(Q/'input-freeze.json'),'recipe_sha256':sha(Q/'inputs/render.py'),'catalog_sha256':sha(Q/'inputs/catalog.json'),'candidate_manifest_sha256':sha(Q/'inputs/candidate_manifest.json'),'entrypoint_sha256':sha(Q/'run_signal_job.py')},'actual_serial_job':{'operation':op,'exit_code':0,'receipt_sha256':sha(copydir/'receipt.json'),'log_sha256':receipt['log_sha256'],'seconds':receipt['seconds']},'actual_counts':{'source_WAV_decoded':20,'signal_checks':metrics['signal_checks'],'catalog_recipe_retention_checks':metrics['catalog_recipe_retention_checks'],'recipe_byte_exact':20,'independent_raw_PCM_rechecks':20,'independent_pair_rechecks':38,'unchanged_input_SHA':35,'legacy_WAV_preserved':5},'mandatory_findings':[],'allows_next_author_step':'Integrate exact reviewed20 plus retained5 Yakuza using INTEGRATION_CONTRACT.md; subsequent runtime/mix evidence and listening required','artistic_status':'ARTISTIC_NOT_LISTENED','actual_listening_performed':False,'runtime_status':'NOT_INTEGRATED_NOT_TESTED','runtime_approval':False,'artistic_approval':False,'full_C01_approval':False,'phase_approval':False,'full_phase_approval':False,'readiness_approval':False,'merge_approval':False,'full_audio_acceptance':'PENDING_ACTUAL_RUNTIME_MIX_AND_ARTISTIC_LISTENING','not_claimed':['Pleasant/quality sound','Audible hero distinctiveness','Safe combined mix from source headroom alone','Loops or music transitions','Native Windows playback','FPS or hardware latency','Universal originality/rights certification']}
save('decision.json',decision)
save('QA_RESUME.json',{'scope':'AUDIO_C01_OFFLINE_SOURCE_SIGNAL_ONLY','status':'COMPLETE_PASS_SIGNAL_ONLY','next':'Author exact source integration per contract; then actual runtime/mix QA and artistic listening independently','listening':'ARTISTIC_NOT_LISTENED','runtime':'NOT_INTEGRATED_NOT_TESTED','phase_approval':False,'do_not_replay_completed_operation':op})
review='''Независимый QA: PASS_SIGNAL_ONLY для 20 исходных WAV C01. Обязательных дефектов формы сигнала или соответствия текущему каталогу не найдено. Это разрешение следующего авторского шага интеграции по INTEGRATION_CONTRACT.md, без приёмки всего C01 или P06.

Проверены реальные файлы, а не только manifest: PCM16 mono 44100 Hz, длительность 0,21–0,31 с, конечное декодирование, RMS/DC/rails, тихие начала/концы, внутренние провалы, плато пиков, собственная оценка true peak и независимый FFmpeg ebur128 peak=true. Исходный декодер wave сопоставлен с ffmpeg float PCM. Все 300 проверок сигналов и 12 каталожных/recipe проверок прошли. Затем QA отдельно пересчитал 20 raw PCM метрик через math.fsum и все 38 пар косинусных сравнений из реальных сохранённых векторов.

RMS −25,179…−18,773 dBFS; sample peak −5,193 dBFS. Максимальная собственная оценка true peak −3,568 dBTP; максимальный округлённый FFmpeg true peak −3,8 dBFS. Это два разных метода с разной интерполяцией; собственный finite-sinc расчёт не заявлен сертифицированным измерителем BS.1770. PCM rails и flat-top clipping не найдены. Максимальный |DC| 0,0004885, максимум первых/последних двух отсчётов 0,0001221; RMS последних 5 мс не выше −66,10 dBFS. Внутренних тихих провалов по объявленному оконному критерию не найдено. Полные числа, пороги и методы находятся в per-asset JSON и metrics.json. Короткие integrated LUFS сохранены только как справочные, без целевой нормализации.

20 маршрутов соответствуют actual catalog: Габар3/Олежка3/ТимкаPrime3/Рыжик3/Тега3/Паша5. TimkaPresent и исключённые для Prime sharp/firearm не появились. Пять старых Yakuza WAV и их маршруты сохранены. Копия math-only recipe в отдельном QA каталоге воспроизвела все20 WAV byte-exact. В проверенном исходнике нет ссылок на заимствованные записи или голоса; это ограниченный вывод о просмотренной recipe, не универсальная правовая сертификация. 35 входных SHA совпали во время job и последующего raw-пересчёта. Ни Game, ни исходные candidates/recipe не изменялись; новые файлы созданы только в назначенном QA отчёте.

Проверена не только уникальность SHA: шесть recipe имеют разные временные структуры thump/cloth, фактические огибающие и спектры измерены по всем20 сигналам; вычислены38 пар общих категорий. Близкие огибающие Oleg/Pasha (blunt cosine0,9971, unarmed0,9954) отмечены как приоритет будущего сравнительного прослушивания. Их spectral cosine0,6825/0,6713 отличается; численные признаки не доказывают ни слышимую одинаковость, ни убедительную индивидуальность. Утверждений о приятном или качественном звучании нет.

Работу выполнил единственный канонический serial Controller job0c23ecf71f324a1c8872cc80ece7bd87: receipt exit0, 9,209с; SHA output.log и argv подтверждены. input.json хранит начальный RUNNING/unconsumed submission, поэтому не используется как терминальная квитанция. Read-only history подтверждает завершение с code0; consumed сообщён родительским Controller. QA не запускал Controller или повторный job. Исходный entrypoint и input freeze сохранились. Локальные дубликаты WAV от reproduction оставлены вне portable manifest; SHA оригиналов сохранены во freeze и результатах.

Фактического прослушивания не было: в обнаруженных инструментах нет средства для аудиопрослушивания; transcript/metadata-инструменты не использованы вместо слуха. Статус ARTISTIC_NOT_LISTENED. Эти20 источников ещё не импортированы и не воспроизводились Godot; runtime и mixer не проверены. Source headroom не гарантирует отсутствие клиппинга при суммировании, изменении gain/pitch или на фоне музыки. Новые dry single shots не требуют loop join; старые музыкальные переходы и loop gates этой проверкой не закрываются. Следующие необходимые доказательства — реальный import и cue/playback/once/cancel/authority, PCM игрового микса при конкуренции и музыке, затем художественное прослушивание исходников и микса. Полный C01, P06/P07, readiness, exports, merge, native Windows, FPS и задержка оборудования не приняты.
'''
(Q/'review.md').write_text(review)
# Manifest is relative and portable. Exclude derivative WAV copies and self-referential inventories.
excluded={'artifacts.json','FINAL_HASHES.json'}
files=[]
for p in sorted(Q.rglob('*')):
 if not p.is_file() or p.name in excluded or 'recipe-reproduction-01' in p.relative_to(Q).parts:continue
 files.append({'path':p.relative_to(Q).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
save('artifacts.json',{'schema':1,'scope':'OWNED_PORTABLE_C01_SIGNAL_QA_EVIDENCE','files':files,'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),'excluded':['recipe-reproduction-01 derivative WAV/manifest copies; original candidate WAV stay at input-freeze paths with exactSHA','artifacts.json self','FINAL_HASHES.json self'],'raw_original_candidates':'20 existing source files are not republished/copied; input-freeze.json and per-asset JSON bind exact hashes; recipe snapshot permits offline reproduction'})
for x in files:assert sha(Q/x['path'])==x['sha256']
save('FINAL_HASHES.json',{'scope':'IMMUTABLE_C01_SIGNAL_ONLY_FINAL','status':'PASS_SIGNAL_ONLY','file_count':len(files),'portable_bytes':sum(x['bytes'] for x in files),'sha256':{n:sha(Q/n) for n in ['decision.json','review.md','artifacts.json','metrics.json','findings.json','input-freeze.json','job-manifest.json','run_signal_job.py','INTEGRATION_CONTRACT.md','job-result.json']}})
print(json.dumps(load(Q/'FINAL_HASHES.json'),ensure_ascii=False,indent=2))
