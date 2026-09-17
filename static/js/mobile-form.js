document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // GERENCIAMENTO DE TEMA (CLARO / ESCURO)
  // ==========================================
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  const themeText = document.getElementById('themeText');

  function getPreferredTheme() {
    const saved = localStorage.getItem('app_theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app_theme', theme);
    const mThemeMoon = document.getElementById('mThemeMoon');
    const mThemeSun = document.getElementById('mThemeSun');
    if (mThemeMoon && mThemeSun && themeText) {
      if (theme === 'dark') {
        mThemeMoon.style.display = 'none';
        mThemeSun.style.display = 'block';
        themeText.textContent = 'Claro';
      } else {
        mThemeMoon.style.display = 'block';
        mThemeSun.style.display = 'none';
        themeText.textContent = 'Escuro';
      }
    }
  }

  applyTheme(getPreferredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // ==========================================
  // ETAPAS DO FORMULÁRIO (WIZARD)
  // ==========================================
  let currentStep = 1;
  const totalSteps = 6;
  let isCpfChecking = false;
  let isCpfValid = false;

  const progressBar = document.getElementById('progressBar');
  const stepNumberEl = document.getElementById('stepNumber');
  const stepNameEl = document.getElementById('stepName');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnSubmit = document.getElementById('btnSubmit');
  const form = document.getElementById('formCandidatura');

  const stepNames = [
    '1. Vaga e Unidade',
    '2. Dados Pessoais',
    '3. Documentos e Medidas',
    '4. Experiência Profissional',
    '5. Saúde e Disponibilidade',
    '6. Termo e Assinatura'
  ];

  // Forçar apenas letras e espaços em nomes
  const inputsApenasLetras = document.querySelectorAll('.apenas-letras');
  inputsApenasLetras.forEach(input => {
    input.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/[^a-zA-Z\u00C0-\u017F\s]/g, '');
    });
  });

  // CPF Mask & Validação
  const inputCpf = document.getElementById('cpf');
  const cpfError = document.getElementById('cpfError');

  if (inputCpf) {
    inputCpf.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 11) v = v.substring(0, 11);

      if (v.length > 9) {
        v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
      } else if (v.length > 6) {
        v = v.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
      } else if (v.length > 3) {
        v = v.replace(/(\d{3})(\d{1,3})/, '$1.$2');
      }
      e.target.value = v;

      if (v.length === 14) {
        validarCpfApi(v);
      } else {
        isCpfValid = false;
        limparErroCpf();
      }
    });

    inputCpf.addEventListener('blur', () => {
      if (inputCpf.value.length === 14) {
        validarCpfApi(inputCpf.value);
      }
    });
  }

  function mostrarErroCpf(msg) {
    if (cpfError) {
      cpfError.textContent = msg;
      cpfError.style.display = 'block';
    }
    inputCpf.classList.add('is-invalid');
    inputCpf.classList.remove('is-valid');
  }

  function limparErroCpf() {
    if (cpfError) {
      cpfError.style.display = 'none';
    }
    inputCpf.classList.remove('is-invalid');
  }

  async function validarCpfApi(cpfFormatado) {
    isCpfChecking = true;
    try {
      const res = await fetch('/api/validar-cpf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cpf: cpfFormatado })
      });
      const data = await res.json();
      if (!data.valido) {
        mostrarErroCpf(data.mensagem || 'CPF inválido.');
        isCpfValid = false;
      } else if (data.existe) {
        mostrarErroCpf(data.mensagem || 'CPF já cadastrado no sistema.');
        isCpfValid = false;
      } else {
        limparErroCpf();
        inputCpf.classList.add('is-valid');
        isCpfValid = true;
      }
    } catch (err) {
      console.error(err);
      isCpfValid = false;
      mostrarErroCpf('Não foi possível validar o CPF. Verifique sua conexão.');
    } finally {
      isCpfChecking = false;
    }
  }

  // Telefone Mask
  const inputsTelefone = document.querySelectorAll('.mask-telefone');
  inputsTelefone.forEach(input => {
    input.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 11) v = v.substring(0, 11);

      if (v.length > 10) {
        v = v.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
      } else if (v.length > 5) {
        v = v.replace(/^(\d{2})(\d{4})(\d{0,4})$/, '($1) $2-$3');
      } else if (v.length > 2) {
        v = v.replace(/^(\d{2})(\d{0,5})$/, '($1) $2');
      } else if (v.length > 0) {
        v = v.replace(/^(\d*)$/, '($1');
      }
      e.target.value = v;
    });
  });

  // CEP Mask + ViaCEP
  const inputCep = document.getElementById('cep');
  if (inputCep) {
    inputCep.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 8) v = v.substring(0, 8);
      if (v.length > 5) {
        v = v.replace(/^(\d{5})(\d{1,3})$/, '$1-$2');
      }
      e.target.value = v;

      if (v.length === 9) {
        buscarCep(v.replace('-', ''));
      }
    });
  }

  async function buscarCep(cepDigitos) {
    try {
      const res = await fetch(`https://viacep.com.br/ws/${cepDigitos}/json/`);
      const data = await res.json();
      if (!data.erro) {
        if (data.logradouro) document.getElementById('endereco').value = data.logradouro;
        if (data.bairro) document.getElementById('bairro').value = data.bairro;
        if (data.localidade) document.getElementById('cidade').value = data.localidade;
        if (data.uf) document.getElementById('uf').value = data.uf;
        const num = document.getElementById('numero');
        if (num) num.focus();
      }
    } catch (e) {
      console.log('Erro ao buscar CEP', e);
    }
  }

  // Data de Nascimento + Idade
  const inputNascimento = document.getElementById('data_nascimento');
  const inputIdade = document.getElementById('idade');

  if (inputNascimento) {
    inputNascimento.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (v.length > 8) v = v.substring(0, 8);

      if (v.length > 4) {
        v = v.replace(/^(\d{2})(\d{2})(\d{1,4})$/, '$1/$2/$3');
      } else if (v.length > 2) {
        v = v.replace(/^(\d{2})(\d{1,2})$/, '$1/$2');
      }
      e.target.value = v;

      if (v.length === 10) {
        calcularIdade(v);
      }
    });
  }

  function calcularIdade(dataStr) {
    const parts = dataStr.split('/');
    if (parts.length === 3) {
      const dia = parseInt(parts[0], 10);
      const mes = parseInt(parts[1], 10) - 1;
      const ano = parseInt(parts[2], 10);
      const nascimento = new Date(ano, mes, dia);
      const hoje = new Date();

      if (!isNaN(nascimento.getTime())) {
        let anos = hoje.getFullYear() - nascimento.getFullYear();
        const m = hoje.getMonth() - nascimento.getMonth();
        if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
          anos--;
        }
        if (anos >= 14 && anos <= 100 && inputIdade) {
          inputIdade.value = anos;
        }
      }
    }
  }

  // Pretensão Salarial
  const inputSalario = document.getElementById('pretensao_salarial');
  if (inputSalario) {
    inputSalario.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '');
      if (!v) {
        e.target.value = '';
        return;
      }
      let valorNumerico = (parseFloat(v) / 100).toFixed(2);
      e.target.value = 'R$ ' + valorNumerico.replace('.', ',').replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
    });
  }

  // Visibilidade de filhos
  const radioFilhosSim = document.getElementById('filhos_sim');
  const radioFilhosNao = document.getElementById('filhos_nao');
  const boxQtdFilhos = document.getElementById('boxQtdFilhos');

  function atualizarVisibilidadeFilhos() {
    if (radioFilhosSim && radioFilhosSim.checked) {
      boxQtdFilhos.style.display = 'block';
    } else if (boxQtdFilhos) {
      boxQtdFilhos.style.display = 'none';
      document.getElementById('qtd_filhos').value = 0;
    }
  }
  if (radioFilhosSim && radioFilhosNao) {
    radioFilhosSim.addEventListener('change', atualizarVisibilidadeFilhos);
    radioFilhosNao.addEventListener('change', atualizarVisibilidadeFilhos);
  }

  // Visibilidade de Companheiro(a) conforme Estado Civil
  const selectEstadoCivil = document.getElementById('estado_civil');
  const boxCompanheiro = document.getElementById('boxCompanheiro');
  const inputCompanheiro = document.getElementById('companheiro');

  function atualizarEstadoCivil() {
    if (!selectEstadoCivil || !boxCompanheiro) return;
    const val = selectEstadoCivil.value;
    if (val === 'Casado' || val === 'Divorciado' || val === 'Viúvo') {
      boxCompanheiro.style.display = 'block';
    } else {
      boxCompanheiro.style.display = 'none';
      if (inputCompanheiro) inputCompanheiro.value = '';
    }
  }
  if (selectEstadoCivil) {
    selectEstadoCivil.addEventListener('change', atualizarEstadoCivil);
    atualizarEstadoCivil();
  }

  // Visibilidade deficiência PCD
  const defSim = document.getElementById('def_sim');
  const defNao = document.getElementById('def_nao');
  const boxDefDesc = document.getElementById('boxDefDesc');

  function atualizarDeficiencia() {
    if (defSim && defSim.checked) {
      boxDefDesc.style.display = 'block';
    } else if (boxDefDesc) {
      boxDefDesc.style.display = 'none';
    }
  }
  if (defSim && defNao) {
    defSim.addEventListener('change', atualizarDeficiencia);
    defNao.addEventListener('change', atualizarDeficiencia);
  }

  // Visibilidade Perguntas de Saúde (1 a 5)
  const camposSaude = [
    { radioName: 'saude_problema_opcao', boxId: 'boxSaudeProblemaDesc', inputId: 'saude_problema_desc' },
    { radioName: 'saude_medicacao_opcao', boxId: 'boxSaudeMedicacaoDesc', inputId: 'saude_medicacao_desc' },
    { radioName: 'saude_acidente_opcao', boxId: 'boxSaudeAcidenteDesc', inputId: 'saude_acidente_desc' },
    { radioName: 'saude_cirurgia_opcao', boxId: 'boxSaudeCirurgiaDesc', inputId: 'saude_cirurgia_desc' },
    { radioName: 'saude_internado_opcao', boxId: 'boxSaudeInternadoDesc', inputId: 'saude_internado_desc' }
  ];

  camposSaude.forEach(item => {
    const radios = document.querySelectorAll(`input[name="${item.radioName}"]`);
    const box = document.getElementById(item.boxId);
    const input = document.getElementById(item.inputId);

    radios.forEach(radio => {
      radio.addEventListener('change', () => {
        if (radio.value === 'Sim' && radio.checked) {
          if (box) box.style.display = 'block';
          if (input) input.focus();
        } else if (radio.value === 'Não' && radio.checked) {
          if (box) {
            box.style.display = 'none';
            if (input) input.value = '';
          }
        }
      });
    });
  });

  // Visibilidade Conhecido / Parente na Empresa
  const radiosTemConhecido = document.querySelectorAll('input[name="comp_tem_conhecido"]');
  const boxNomeConhecido = document.getElementById('boxNomeConhecido');
  const inputNomeConhecido = document.getElementById('comp_nome_conhecido');

  radiosTemConhecido.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.checked) {
        if (radio.value === 'Não tenho') {
          if (boxNomeConhecido) boxNomeConhecido.style.display = 'none';
          if (inputNomeConhecido) inputNomeConhecido.value = '';
        } else {
          if (boxNomeConhecido) {
            boxNomeConhecido.style.display = 'block';
            if (inputNomeConhecido) inputNomeConhecido.focus();
          }
        }
      }
    });
  });

  // Gerenciamento de Experiências Profissionais Adicionais
  let maxExpVisiveis = 2;
  const btnAddExp = document.getElementById('btnAddExp');

  if (btnAddExp) {
    btnAddExp.addEventListener('click', () => {
      if (maxExpVisiveis === 2) {
        const box3 = document.getElementById('boxExp3');
        if (box3) {
          box3.style.display = 'block';
          maxExpVisiveis = 3;
          box3.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      } else if (maxExpVisiveis === 3) {
        const box4 = document.getElementById('boxExp4');
        if (box4) {
          box4.style.display = 'block';
          maxExpVisiveis = 4;
          btnAddExp.style.display = 'none';
          box4.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    });
  }

  window.removerExperiencia = function(num) {
    const box = document.getElementById(`boxExp${num}`);
    if (box) {
      box.style.display = 'none';
      box.querySelectorAll('input').forEach(inp => inp.value = '');
      if (btnAddExp) btnAddExp.style.display = 'inline-flex';
      if (num === 4 && maxExpVisiveis === 4) maxExpVisiveis = 3;
      if (num === 3 && maxExpVisiveis >= 3) maxExpVisiveis = 2;
    }
  };

  // Sincronização de classe .selected para Radio Cards
  document.querySelectorAll('.radio-card input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', () => {
      const groupName = radio.getAttribute('name');
      document.querySelectorAll(`input[type="radio"][name="${groupName}"]`).forEach(r => {
        const card = r.closest('.radio-card');
        if (card) {
          if (r.checked) {
            card.classList.add('selected');
          } else {
            card.classList.remove('selected');
          }
        }
      });
    });
  });

  // ==========================================
  // NAVEGAÇÃO ENTRE ETAPAS
  // ==========================================
  function updateStepUI() {
    document.querySelectorAll('.step-panel').forEach(panel => {
      panel.classList.remove('active');
    });

    const activePanel = document.getElementById(`step-${currentStep}`);
    if (activePanel) {
      activePanel.classList.add('active');
    }

    const percent = (currentStep / totalSteps) * 100;
    progressBar.style.width = `${percent}%`;
    stepNumberEl.textContent = `Etapa ${currentStep} de ${totalSteps}`;
    stepNameEl.textContent = stepNames[currentStep - 1];

    btnPrev.style.display = currentStep === 1 ? 'none' : 'inline-flex';
    if (currentStep === totalSteps) {
      btnNext.style.display = 'none';
      btnSubmit.style.display = 'inline-flex';
      if (typeof window.resizeSignatureCanvas === 'function') {
        setTimeout(window.resizeSignatureCanvas, 150);
      }
    } else {
      btnNext.style.display = 'inline-flex';
      btnSubmit.style.display = 'none';
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function validateCurrentStep() {
    const currentPanel = document.getElementById(`step-${currentStep}`);
    const requiredInputs = currentPanel.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
      if (!input.value || input.value.trim() === '') {
        input.classList.add('is-invalid');
        isValid = false;
      } else {
        input.classList.remove('is-invalid');
      }
    });

    if (currentStep === 2) {
      if (inputCpf.value.length !== 14 || !isCpfValid) {
        mostrarErroCpf('Informe um CPF válido e sem cadastro prévio.');
        isValid = false;
      }
    }

    if (!isValid) {
      const primeiroInvalido = currentPanel.querySelector('.is-invalid');
      if (primeiroInvalido) {
        primeiroInvalido.focus();
      }
    }

    return isValid;
  }

  btnNext.addEventListener('click', async () => {
    if (currentStep === 2 && isCpfChecking) {
      let checks = 0;
      while (isCpfChecking && checks < 20) {
        await new Promise(r => setTimeout(r, 100));
        checks++;
      }
    }

    if (validateCurrentStep()) {
      if (currentStep < totalSteps) {
        currentStep++;
        updateStepUI();
      }
    }
  });

  btnPrev.addEventListener('click', () => {
    if (currentStep > 1) {
      currentStep--;
      updateStepUI();
    }
  });

  // ==========================================
  // CANVAS DE ASSINATURA TOUCH / MOUSE
  // ==========================================
  const canvas = document.getElementById('signatureCanvas');
  const btnClearSign = document.getElementById('btnClearSign');
  const inputSignature = document.getElementById('assinatura_digital');

  let ctx = null;
  let isDrawing = false;
  let hasSigned = false;

  if (canvas) {
    ctx = canvas.getContext('2d');

    function resizeCanvas() {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * 2;
      canvas.height = rect.height * 2;
      ctx.scale(2, 2);
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    }

    window.addEventListener('resize', resizeCanvas);
    window.resizeSignatureCanvas = resizeCanvas;
    setTimeout(resizeCanvas, 300);

    function getCoordinates(e) {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return {
        x: clientX - rect.left,
        y: clientY - rect.top
      };
    }

    function startDrawing(e) {
      e.preventDefault();
      isDrawing = true;
      hasSigned = true;
      const { x, y } = getCoordinates(e);
      ctx.beginPath();
      ctx.moveTo(x, y);
    }

    function draw(e) {
      if (!isDrawing) return;
      e.preventDefault();
      const { x, y } = getCoordinates(e);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    function stopDrawing() {
      if (isDrawing) {
        isDrawing = false;
        inputSignature.value = canvas.toDataURL('image/png');
      }
    }

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);

    canvas.addEventListener('touchstart', startDrawing, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', stopDrawing);

    if (btnClearSign) {
      btnClearSign.addEventListener('click', (e) => {
        e.preventDefault();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hasSigned = false;
        inputSignature.value = '';
      });
    }
  }

  form.addEventListener('submit', (e) => {
    if (!hasSigned || !inputSignature.value) {
      e.preventDefault();
      alert('Por favor, faça sua assinatura no quadro antes de enviar.');
      return false;
    }
    const checkTermo = document.getElementById('termo_aceite');
    if (checkTermo && !checkTermo.checked) {
      e.preventDefault();
      alert('Você deve aceitar a declaração e o termo de dados para continuar.');
      return false;
    }
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = 'Enviando ficha...';
  });

  updateStepUI();
});
